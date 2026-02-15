"""
Aimbot 激活狀態管理模組
支持多種激活類型：按住啟用、按住停用、切換、使用啟用
"""
import threading
from src.utils.mouse import is_button_pressed

# 全局狀態管理
_activation_states = {
    "main": {
        "toggle_state": False,  # 切換狀態
        "use_enable_state": False,  # 使用啟用狀態
        "last_button_state": False,  # 上次按鈕狀態
        "lock": threading.Lock()  # 線程鎖
    },
    "sec": {
        "toggle_state": False,
        "use_enable_state": False,
        "last_button_state": False,
        "lock": threading.Lock()
    }
}

_BUTTON_NAME_TO_IDX = {
    "left mouse button": 0,
    "right mouse button": 1,
    "middle mouse button": 2,
    "side mouse 4 button": 3,
    "side mouse 5 button": 4,
}


def _normalize_button_idx(button_idx):
    if button_idx is None:
        return None
    try:
        return int(button_idx)
    except Exception:
        key = str(button_idx).strip().lower()
        return _BUTTON_NAME_TO_IDX.get(key, None)


def check_aimbot_activation(button_idx: int, activation_type: str, is_sec: bool = False) -> bool:
    """
    檢查 Aimbot 是否應該激活
    
    Args:
        button_idx: 按鈕索引
        activation_type: 激活類型 ("hold_enable", "hold_disable", "toggle", "use_enable")
        is_sec: 是否為 Sec Aimbot
    
    Returns:
        bool: 是否應該激活
    """
    normalized_idx = _normalize_button_idx(button_idx)
    if normalized_idx is None:
        # Treat invalid button as "not pressed" to keep hold_disable semantics usable.
        current_pressed = False
    else:
        try:
            current_pressed = bool(is_button_pressed(normalized_idx))
        except Exception:
            current_pressed = False
    
    key = "sec" if is_sec else "main"
    state = _activation_states[key]
    
    with state["lock"]:
        last_pressed = state["last_button_state"]
        
        if activation_type == "hold_enable":
            # 按住啟用：按鈕按下時激活
            result = current_pressed
        
        elif activation_type == "hold_disable":
            # 按住停用：按鈕按下時停用，放開時激活
            result = not current_pressed
        
        elif activation_type == "toggle":
            # 切換：按鈕從未按下變為按下時切換狀態
            if not last_pressed and current_pressed:
                # 按鈕剛按下，切換狀態
                state["toggle_state"] = not state["toggle_state"]
            result = state["toggle_state"]
        
        elif activation_type == "use_enable":
            # 使用啟用：按鈕從未按下變為按下時啟用，再次按下時停用
            if not last_pressed and current_pressed:
                # 按鈕剛按下，切換狀態
                state["use_enable_state"] = not state["use_enable_state"]
            result = state["use_enable_state"]
        
        else:
            # 默認：按住啟用
            result = current_pressed
        
        # 更新上次按鈕狀態
        state["last_button_state"] = current_pressed
    
    return result


def reset_activation_state(is_sec: bool = False):
    """
    重置激活狀態（用於切換和使用啟用模式）
    
    Args:
        is_sec: 是否為 Sec Aimbot
    """
    key = "sec" if is_sec else "main"
    state = _activation_states[key]
    with state["lock"]:
        state["toggle_state"] = False
        state["use_enable_state"] = False
        state["last_button_state"] = False
