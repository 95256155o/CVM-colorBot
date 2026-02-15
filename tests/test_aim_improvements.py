import math

from src.aim_system.Triggerbot import evaluate_trigger_metrics, update_confirm_counter
from src.aim_system.normal import compute_silent_delta
from src.aim_system.target_smoother import TargetSmoother


def _target(x, y):
    return (float(x), float(y), math.hypot(float(x), float(y)), None, None)


def test_silent_multiplier_applied():
    dx, dy = compute_silent_delta(5, -3, multiplier=2.0, max_speed=1000.0)
    assert abs(dx - 10) <= 1
    assert abs(dy - (-6)) <= 1


def test_trigger_pixel_threshold():
    detected_low, ratio_low = evaluate_trigger_metrics(
        pixel_count=3,
        roi_area=120,
        min_pixels=4,
        min_ratio=0.03,
    )
    assert not detected_low
    assert ratio_low < 0.03

    detected_ratio_fail, ratio_fail = evaluate_trigger_metrics(
        pixel_count=5,
        roi_area=500,
        min_pixels=4,
        min_ratio=0.03,
    )
    assert not detected_ratio_fail
    assert ratio_fail < 0.03

    detected_ok, ratio_ok = evaluate_trigger_metrics(
        pixel_count=20,
        roi_area=400,
        min_pixels=4,
        min_ratio=0.03,
    )
    assert detected_ok
    assert ratio_ok >= 0.03

    count, confirmed = update_confirm_counter(0, detected_ok, confirm_frames=2)
    assert count == 1
    assert not confirmed
    count, confirmed = update_confirm_counter(count, detected_ok, confirm_frames=2)
    assert count == 2
    assert confirmed
    count, confirmed = update_confirm_counter(count, False, confirm_frames=2)
    assert count == 0
    assert not confirmed


def test_target_hysteresis():
    smoother = TargetSmoother(ema_alpha=1.0, switch_confirm_frames=3, switch_radius_px=5.0)
    center_x, center_y = 0.0, 0.0

    first = smoother.stabilize([_target(10, 0)], center_x, center_y)[0]
    assert int(round(first[0])) == 10

    for candidate in (_target(30, 0), _target(10, 0), _target(30, 0), _target(10, 0), _target(30, 0)):
        out = smoother.stabilize([candidate], center_x, center_y)[0]
        assert int(round(out[0])) == 10

    out = smoother.stabilize([_target(10, 0)], center_x, center_y)[0]
    assert int(round(out[0])) == 10
    out = smoother.stabilize([_target(30, 0)], center_x, center_y)[0]
    assert int(round(out[0])) == 10
    out = smoother.stabilize([_target(30, 0)], center_x, center_y)[0]
    assert int(round(out[0])) == 10
    out = smoother.stabilize([_target(30, 0)], center_x, center_y)[0]
    assert int(round(out[0])) == 30
