from src.utils.debug_logger import log_print
import cv2
import numpy as np

from src.utils.config import config


_model = None
_class_names = {}
HSV_MIN = None
HSV_MAX = None


def test():
    log_print("HSV Detection test initialized")
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    _ = cv2.cvtColor(dummy_img, cv2.COLOR_BGR2HSV)
    log_print("HSV conversion done")


def load_model(model_path=None):
    global _model, _class_names, HSV_MIN, HSV_MAX
    config.model_load_error = ""

    try:
        log_print("Loading HSV parameters...")
        # Wider HSV presets to better tolerate compression/lighting variance.
        yellow = [18, 80, 80, 40, 255, 255]
        purple = [125, 60, 80, 170, 255, 255]

        if config.color == "yellow":
            HSV_MIN = np.array([yellow[0], yellow[1], yellow[2]], dtype=np.uint8)
            HSV_MAX = np.array([yellow[3], yellow[4], yellow[5]], dtype=np.uint8)
            log_print("Loaded HSV for yellow")
        elif config.color == "purple":
            HSV_MIN = np.array([purple[0], purple[1], purple[2]], dtype=np.uint8)
            HSV_MAX = np.array([purple[3], purple[4], purple[5]], dtype=np.uint8)
            log_print("Loaded HSV for purple")
        elif config.color == "custom":
            HSV_MIN = np.array(
                [
                    getattr(config, "custom_hsv_min_h", 0),
                    getattr(config, "custom_hsv_min_s", 0),
                    getattr(config, "custom_hsv_min_v", 0),
                ],
                dtype=np.uint8,
            )
            HSV_MAX = np.array(
                [
                    getattr(config, "custom_hsv_max_h", 179),
                    getattr(config, "custom_hsv_max_s", 255),
                    getattr(config, "custom_hsv_max_v", 255),
                ],
                dtype=np.uint8,
            )
            log_print(f"Loaded custom HSV: MIN={HSV_MIN}, MAX={HSV_MAX}")
        else:
            raise ValueError(f"Unknown color {config.color}")

        _model = (HSV_MIN, HSV_MAX)
        _class_names = {"color": "Target Color"}
        config.model_classes = list(_class_names.values())
        config.model_file_size = 0
        return _model, _class_names
    except Exception as exc:
        config.model_load_error = f"Failed to load HSV params: {exc}"
        _model, _class_names = None, {}
        return None, {}


def reload_model(model_path=None):
    return load_model(model_path)


def has_color_vertical_line(mask, x, y1, y2):
    x = int(max(0, min(x, mask.shape[1] - 1)))
    y1 = int(max(0, min(y1, mask.shape[0])))
    y2 = int(max(0, min(y2, mask.shape[0])))
    if y2 <= y1:
        return False
    line = mask[y1:y2, x]
    return bool(np.any(line > 0))


def _bbox_area(rect):
    _, _, w, h = rect
    return max(0, int(w)) * max(0, int(h))


def _touches_border(rect, img_w, img_h, margin=1):
    x, y, w, h = rect
    return (
        x <= margin
        or y <= margin
        or (x + w) >= (img_w - margin)
        or (y + h) >= (img_h - margin)
    )


def _boxes_overlap(r1, r2):
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    return (x1 < x2 + w2 and x1 + w1 > x2) and (y1 < y2 + h2 and y1 + h1 > y2)


def _overlap_len(a0, a1, b0, b1):
    return max(0, min(a1, b1) - max(a0, b0))


def _boxes_should_merge(r1, r2, dist_threshold):
    if _boxes_overlap(r1, r2):
        return True

    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    x1r, y1r = x1 + w1, y1 + h1
    x2r, y2r = x2 + w2, y2 + h2

    h_gap = max(0, max(x1, x2) - min(x1r, x2r))
    v_gap = max(0, max(y1, y2) - min(y1r, y2r))
    h_overlap = _overlap_len(x1, x1r, x2, x2r)
    v_overlap = _overlap_len(y1, y1r, y2, y2r)

    a1 = max(1, _bbox_area(r1))
    a2 = max(1, _bbox_area(r2))
    size_ratio = min(a1, a2) / max(a1, a2)
    # Merge mainly fragment-like splits; avoid merging similarly sized players.
    small_fragment = size_ratio <= 0.80
    if not small_fragment:
        return False

    close_h = h_gap <= dist_threshold and v_overlap >= 0.60 * min(h1, h2)
    close_v = v_gap <= dist_threshold and h_overlap >= 0.60 * min(w1, w2)
    return close_h or close_v


def merge_close_rects(rects, centers, dist_threshold=None):
    if dist_threshold is None:
        dist_threshold = int(getattr(config, "detection_merge_distance", 12))
    dist_threshold = int(max(0, min(dist_threshold, 18)))

    merged = []
    merged_centers = []
    used = [False] * len(rects)

    for i, (r1, c1) in enumerate(zip(rects, centers)):
        if used[i]:
            continue

        x1, y1, w1, h1 = r1
        nx1, ny1 = x1, y1
        nx2, ny2 = x1 + w1, y1 + h1

        changed = True
        while changed:
            changed = False
            current_rect = (nx1, ny1, nx2 - nx1, ny2 - ny1)
            for j, r2 in enumerate(rects):
                if i == j or used[j]:
                    continue
                if _boxes_should_merge(current_rect, r2, dist_threshold):
                    x2, y2, w2, h2 = r2
                    nx1 = min(nx1, x2)
                    ny1 = min(ny1, y2)
                    nx2 = max(nx2, x2 + w2)
                    ny2 = max(ny2, y2 + h2)
                    used[j] = True
                    changed = True

        used[i] = True
        final_w = max(1, nx2 - nx1)
        final_h = max(1, ny2 - ny1)
        final_cx = int(nx1 + final_w // 2)
        final_cy = int(ny1 + final_h // 2)
        merged.append((nx1, ny1, final_w, final_h))
        merged_centers.append((final_cx, final_cy))

    sort_idx = sorted(range(len(merged)), key=lambda idx: _bbox_area(merged[idx]), reverse=True)
    merged = [merged[idx] for idx in sort_idx]
    merged_centers = [merged_centers[idx] for idx in sort_idx]

    return merged, merged_centers


def triggerbot_detect(model, roi):
    if model is None or roi is None:
        return False
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, model[0], model[1])
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return bool(np.any(mask > 0))


def perform_detection(model, image):
    if model is None or image is None:
        return [], None

    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    raw_mask = cv2.inRange(hsv_img, model[0], model[1])
    mask = raw_mask.copy()

    # Reference-like morphology path (close + dilate) is the default because it
    # keeps thin color edges that OPEN often removes completely.
    morph_mode = str(getattr(config, "detection_morph_mode", "legacy")).strip().lower()
    if morph_mode == "stable":
        open_kernel_size = int(getattr(config, "detection_open_kernel", 3))
        close_kernel_size = int(getattr(config, "detection_close_kernel", 5))
        blur_kernel_size = int(getattr(config, "detection_mask_blur", 3))
        open_kernel_size = max(1, min(open_kernel_size, 9))
        close_kernel_size = max(1, min(close_kernel_size, 13))
        blur_kernel_size = max(1, min(blur_kernel_size, 7))
        if open_kernel_size % 2 == 0:
            open_kernel_size += 1
        if close_kernel_size % 2 == 0:
            close_kernel_size += 1
        if blur_kernel_size % 2 == 0:
            blur_kernel_size += 1
        open_kernel = np.ones((open_kernel_size, open_kernel_size), np.uint8)
        close_kernel = np.ones((close_kernel_size, close_kernel_size), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_kernel)
        if blur_kernel_size >= 3:
            mask = cv2.medianBlur(mask, blur_kernel_size)
    else:
        legacy_kernel_w = int(getattr(config, "detection_legacy_kernel_w", 15))
        legacy_kernel_h = int(getattr(config, "detection_legacy_kernel_h", 9))
        legacy_dilate_iterations = int(getattr(config, "detection_legacy_dilate_iterations", 1))
        legacy_kernel_w = max(1, min(legacy_kernel_w, 40))
        legacy_kernel_h = max(1, min(legacy_kernel_h, 30))
        legacy_dilate_iterations = max(0, min(legacy_dilate_iterations, 3))
        legacy_kernel = np.ones((legacy_kernel_h, legacy_kernel_w), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, legacy_kernel)
        if legacy_dilate_iterations > 0:
            mask = cv2.dilate(mask, legacy_kernel, iterations=legacy_dilate_iterations)

    # If morphology erased all pixels, fall back to raw mask instead of returning empty.
    if cv2.countNonZero(mask) == 0 and cv2.countNonZero(raw_mask) > 0:
        mask = raw_mask

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects, centers = [], []

    img_h, img_w = image.shape[:2]
    frame_area = max(1, img_h * img_w)
    min_bbox_area = int(getattr(config, "detection_min_bbox_area", max(36, int(frame_area * 0.00025))))
    min_contour_area = float(
        getattr(config, "detection_min_contour_area", max(8, int(frame_area * 0.00008)))
    )
    min_fill_ratio = float(getattr(config, "detection_min_fill_ratio", 0.03))
    edge_reject_area = int(
        getattr(config, "detection_edge_reject_area", max(80, int(frame_area * 0.0006)))
    )
    edge_min_contour_area = float(
        getattr(config, "detection_edge_min_contour_area", max(30, int(frame_area * 0.0002)))
    )
    edge_min_side = int(getattr(config, "detection_edge_min_side", 4))
    border_margin = int(getattr(config, "detection_border_margin", 0))
    min_w = int(getattr(config, "detection_min_width", 3))
    min_h = int(getattr(config, "detection_min_height", 4))
    min_aspect = float(getattr(config, "detection_min_aspect", 0.04))
    max_aspect = float(getattr(config, "detection_max_aspect", 6.0))
    require_vertical_line = bool(getattr(config, "detection_require_vertical_line", False))
    min_contour_points = int(getattr(config, "detection_min_contour_points", 5))

    if morph_mode != "stable":
        # Prevent stale strict settings from killing detection in legacy mode.
        min_bbox_area = min(min_bbox_area, max(48, int(frame_area * 0.00045)))
        min_contour_area = min(min_contour_area, max(10, int(frame_area * 0.00010)))
        min_fill_ratio = min(min_fill_ratio, 0.08)

    for c in contours:
        if len(c) < min_contour_points:
            continue

        x, y, w, h = cv2.boundingRect(c)
        bbox_area = int(w) * int(h)
        contour_area = float(cv2.contourArea(c))
        if contour_area < min_contour_area:
            continue
        if bbox_area < min_bbox_area:
            continue
        if int(w) < min_w or int(h) < min_h:
            continue

        fill_ratio = contour_area / max(float(bbox_area), 1.0)
        if fill_ratio < min_fill_ratio:
            continue

        aspect = float(w) / max(float(h), 1.0)
        if aspect < min_aspect or aspect > max_aspect:
            continue

        touches_border = _touches_border((x, y, w, h), img_w, img_h, margin=border_margin)
        if touches_border:
            if bbox_area < edge_reject_area:
                continue
            if contour_area < edge_min_contour_area:
                continue
            if min(int(w), int(h)) < edge_min_side:
                continue

        cx, cy = x + w // 2, y + h // 2
        if require_vertical_line and not has_color_vertical_line(mask, cx, y, y + h):
            continue

        rects.append((x, y, w, h))
        centers.append((cx, cy))

    # Fallback pass on raw mask with minimal checks if filtered pass found nothing.
    if not rects and cv2.countNonZero(raw_mask) > 0:
        raw_contours, _ = cv2.findContours(raw_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        loose_min_area = max(20, int(min_bbox_area * 0.5))
        for c in raw_contours:
            x, y, w, h = cv2.boundingRect(c)
            if int(w) * int(h) < loose_min_area:
                continue
            cx, cy = x + w // 2, y + h // 2
            rects.append((x, y, w, h))
            centers.append((cx, cy))

    if not rects:
        return [], mask

    rects_centers = sorted(zip(rects, centers), key=lambda rc: _bbox_area(rc[0]), reverse=True)
    rects = [rc[0] for rc in rects_centers]
    centers = [rc[1] for rc in rects_centers]

    merged_rects, _ = merge_close_rects(rects, centers)
    return [{"class": "player", "bbox": r, "confidence": 1.0} for r in merged_rects], mask


def get_class_names():
    return _class_names


def get_model_size(model_path=None):
    return 0
