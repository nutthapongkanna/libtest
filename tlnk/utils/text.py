"""
Text utilities.
"""
import re
import unicodedata
from typing import Optional


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_special_chars(text: str, keep: str = "") -> str:
    pattern = rf"[^a-zA-Z0-9\s{re.escape(keep)}]"
    return re.sub(pattern, "", text)


def to_snake_case(text: str) -> str:
    text = re.sub(r"[\s\-]+", "_", text.strip().lower())
    return re.sub(r"[^\w]", "", text)


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def is_empty(value: Optional[str]) -> bool:
    return value is None or str(value).strip() == ""
