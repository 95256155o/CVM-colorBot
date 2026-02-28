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
        pass # 乾乾淨淨，不需要任何狀態了！

    @staticmethod
    def compute_ncaf_factor(distance: float, snap_radius: float, near_radius: float, alpha: float, snap_boost: float) -> float:
        if snap_radius < near_radius:
            snap_radius, near_radius = near_radius, snap_radius

        # 🛡️ 守護底線：圈外絕對不給倍率 (回傳 0.0)
        if distance > snap_radius:
            return 0.0

        if distance > near_radius:
            gap = snap_radius - near_radius
            if gap < 1e-6:
                return snap_boost
            t = (snap_radius - distance) / gap
            return 1.0 + t * (snap_boost - 1.0)

        if near_radius > 1e-6:
            return snap_boost * (distance / near_radius) ** max(0.0, alpha)
        return snap_boost

    def compute_ncaf_delta(self, dx: float, dy: float, near_radius: float, snap_radius: float, alpha: float, snap_boost: float, max_step: float) -> Tuple[float, float]:
        distance = math.hypot(dx, dy)
        
        # 🛡️ 守護底線：圈外不動作 / 貼臉不動作
        if distance > snap_radius or distance <= 5.0:  # 死區可以縮小到 5.0，因為是手動按鍵
            return 0.0, 0.0

        factor = self.compute_ncaf_factor(distance, snap_radius, near_radius, alpha, snap_boost)
        
        # 既然是手動觸發，速度要快，可以直接把 factor 乘大
        new_dx = dx * factor
        new_dy = dy * factor

        step = math.hypot(new_dx, new_dy)
        if max_step > 0 and step > max_step:
            scale = max_step / step
            new_dx *= scale
            new_dy *= scale
            
        return new_dx, new_dy

_ncaf_singleton: Optional[NCAFController] = None

def get_ncaf_controller() -> NCAFController:
    global _ncaf_singleton
    if _ncaf_singleton is None:
        _ncaf_singleton = NCAFController()
    return _ncaf_singleton
