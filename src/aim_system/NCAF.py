import math
import time
from typing import Optional, Tuple


class NCAFController:
    """Nonlinear Close-Aim with Focus (NCAF) controller.

    Implements a 3-zone speed curve (from outside to inside):

        ┌─────────────────────────────┐
        │  Snap Radius (outer, dashed)│   Zone 1: factor = 1.0
        │  ┌───────────────────────┐  │
        │  │ Near Radius (inner)   │  │   Zone 2: smooth transition
        │  │  ┌──── ＋ ────┐       │  │
        │  │  │ Target Ctr │       │  │   Zone 3: α exponent + snap_boost
        │  │  └────────────┘       │  │
        │  └───────────────────────┘  │
        └─────────────────────────────┘

      - Snap Radius (outer): overall engagement zone
      - Near Radius (inner): precision zone, speed tapered by exponent α
      - Snap Boost Factor: base multiplier inside the near zone
      - α (Speed Curve Exponent): controls how aggressively speed drops near center
      - Max Step: limits per-frame movement magnitude

    Note: snap_radius should be >= near_radius. If not, they are auto-swapped.
    """

    def __init__(self) -> None:
        """Initialize NCAF controller with Smart Force state tracking."""
        # [NEW] 用來追蹤「玩家滑鼠移動趨勢」的狀態
        self.last_dx = 0.0
        self.last_dy = 0.0
        self.last_time = time.time()

        # [NEW] 「神秘推力 (Smart Force)」的狀態機參數
        self.force_active = False
        self.force_start_time = 0.0
        
        # --- 你可以自由微調這四個「爽度」參數 ---
        self.force_duration = 0.18      # 每次推力持續時間 (300ms)
        self.force_cooldown = 0.4      # 推力冷卻時間 (1秒觸發一次)
        self.force_max_mult = 1.85      # 推力爆發時的最大倍率 (預設2.5倍，越大吸得越猛)
        self.flick_threshold = 0.6     # 意圖判定閾值 (數字越小越容易觸發推力)
        # ----------------------------------------
        
        self.last_force_time = 0.0

    @staticmethod
    def compute_ncaf_factor(distance: float,
                            snap_radius: float,
                            near_radius: float,
                            alpha: float,
                            snap_boost: float) -> float:
        # (保持完全不變)
        if snap_radius < near_radius:
            snap_radius, near_radius = near_radius, snap_radius

        if distance > snap_radius:
            return 1.0

        if distance > near_radius:
            gap = snap_radius - near_radius
            if gap < 1e-6:
                return snap_boost
            t = (snap_radius - distance) / gap
            return 1.0 + t * (snap_boost - 1.0)

        if near_radius > 1e-6:
            return snap_boost * (distance / near_radius) ** max(0.0, alpha)
        return snap_boost

    def compute_ncaf_delta(self,
                            dx: float,
                            dy: float,
                            near_radius: float,
                            snap_radius: float,
                            alpha: float,
                            snap_boost: float,
                            max_step: float,
                            min_speed_multiplier: float = 0.01,
                            max_speed_multiplier: float = 10.0) -> Tuple[float, float]:
        
        current_time = time.time()
        distance = math.hypot(dx, dy)
        
        # 只要目標距離準星中心小於等於 20 像素，系統就當作「完美命中」，徹底放棄微調！
        if distance <= 20.0:
            self.last_dx, self.last_dy = dx, dy
            return 0.0, 0.0

        # ==========================================
        #[NEW] 1. 計算玩家意圖 (Intent Detection)
        # ==========================================
        # 假設目標移動不大，上一幀的 dx 減去當前的 dx，近似於玩家的滑鼠移動量
        mouse_move_x = self.last_dx - dx
        mouse_move_y = self.last_dy - dy
        
        # 內積 (Dot Product)：判斷玩家移動方向與目標方向是否一致
        dot_product = (mouse_move_x * dx) + (mouse_move_y * dy)
        
        # 將內積標準化，得到玩家「甩向目標的強度」
        intent_strength = dot_product / (distance + 1e-6)

        # ==========================================
        # [NEW] 2. 觸發「300ms 神秘推力」
        # ==========================================
        if not self.force_active:
            # 確保過了 1 秒的冷卻時間
            if (current_time - self.last_force_time) > self.force_cooldown:
                # 只有當玩家主動往目標方向「甩」超過閾值時，才啟動推力！
                if intent_strength > self.flick_threshold:
                    self.force_active = True
                    self.force_start_time = current_time
                    # 你可以把下面這行取消註解，在終端機看觸發時機
                    # print("🚀 [NCAF] 偵測到甩槍意圖，啟動 300ms 神秘推力！")
                    
        # ==========================================
        #[NEW] 3. 計算推力的動態曲線 (Sine Wave)
        # ==========================================
        force_multiplier = 1.0
        if self.force_active:
            elapsed = current_time - self.force_start_time
            if elapsed > self.force_duration:
                # 推力結束，進入冷卻
                self.force_active = False
                self.last_force_time = current_time
            else:
                # 緊急煞車機制：如果推力期間，玩家突然往反方向用力拉 (比如敵人死了他要換目標)
                if intent_strength < -self.flick_threshold * 2:
                    self.force_active = False  # 立刻中斷推力，把控制權還給玩家
                else:
                    # 畫一個完美的 Sine 曲線：0 -> 1 -> 0
                    # 這樣推力介入和退出的瞬間會極度平滑，不會有「頓挫感」
                    progress = elapsed / self.force_duration
                    curve = math.sin(progress * math.pi)
                    
                    # 將曲線映射到倍率上 (例如 1.0 到 2.5 倍)
                    force_multiplier = 1.0 + (curve * (self.force_max_mult - 1.0))

        # ------------------------------------------
        # 4. 原本的 NCAF 核心運算
        # ------------------------------------------
        factor = self.compute_ncaf_factor(distance, snap_radius, near_radius, alpha, snap_boost)
        factor = max(min_speed_multiplier, min(factor, max_speed_multiplier))

        # [NEW] 把算出來的 NCAF factor 乘上我們的 神秘推力倍率
        final_factor = factor * force_multiplier

        new_dx = dx * final_factor
        new_dy = dy * final_factor

        # 限制最大單步移動
        step = math.hypot(new_dx, new_dy)
        if max_step > 0 and step > max_step:
            scale = max_step / step
            new_dx *= scale
            new_dy *= scale
            
        # [NEW] 記錄這一幀的狀態，給下一幀計算 Intent 用
        self.last_dx = dx
        self.last_dy = dy
        self.last_time = current_time

        return new_dx, new_dy


_ncaf_singleton: Optional[NCAFController] = None

def get_ncaf_controller() -> NCAFController:
    global _ncaf_singleton
    if _ncaf_singleton is None:
        _ncaf_singleton = NCAFController()
    return _ncaf_singleton
