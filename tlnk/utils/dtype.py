"""
Data type casting utilities.
"""
from typing import Optional, Any


def to_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(float(str(value).replace(",", "").strip()))
    except (ValueError, TypeError):
        return default


def to_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return default


def to_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() in ("true", "yes", "1", "y"):
            return True
        if value.lower() in ("false", "no", "0", "n"):
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return None


def to_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()
