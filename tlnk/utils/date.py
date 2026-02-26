"""
Date utilities.
"""
from datetime import datetime
from typing import Optional

COMMON_FORMATS = [
    "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d",
    "%d %b %Y", "%d %B %Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
]


def parse_date(value: str, formats: Optional[list] = None) -> Optional[datetime]:
    for fmt in (formats or COMMON_FORMATS):
        try:
            return datetime.strptime(value.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def to_iso(value: str) -> Optional[str]:
    dt = parse_date(value)
    return dt.strftime("%Y-%m-%d") if dt else None


def format_date(value: str, output_fmt: str = "%d/%m/%Y") -> Optional[str]:
    dt = parse_date(value)
    return dt.strftime(output_fmt) if dt else None


def is_valid_date(value: str) -> bool:
    return parse_date(value) is not None
