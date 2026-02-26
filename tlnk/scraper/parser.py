"""
HTML/JSON parser.
"""
from typing import Optional, List, Dict, Any
from ..utils import get_logger

logger = get_logger(__name__)


class ParserError(Exception):
    pass


class HtmlParser:
    """
    Parse HTML content using BeautifulSoup.

    Usage:
        parser = HtmlParser(html)
        title = parser.find_text("h1")
        rows  = parser.find_table("table")
    """

    def __init__(self, html: str):
        if not html or not html.strip():
            raise ParserError("HTML content cannot be empty.")
        try:
            from bs4 import BeautifulSoup
            self._soup = BeautifulSoup(html, "html.parser")
        except ImportError:
            raise ImportError("beautifulsoup4 is required. Run: pip install beautifulsoup4")

    def find_text(self, selector: str) -> Optional[str]:
        el = self._soup.select_one(selector)
        return el.get_text(strip=True) if el else None

    def find_all_text(self, selector: str) -> List[str]:
        return [el.get_text(strip=True) for el in self._soup.select(selector)]

    def find_attr(self, selector: str, attr: str) -> Optional[str]:
        el = self._soup.select_one(selector)
        return el.get(attr) if el else None

    def find_all_attr(self, selector: str, attr: str) -> List[str]:
        return [el.get(attr) for el in self._soup.select(selector) if el.get(attr)]

    def find_table(self, selector: str = "table") -> List[Dict[str, str]]:
        table = self._soup.select_one(selector)
        if not table:
            return []
        headers = [th.get_text(strip=True) for th in table.select("th")]
        rows = []
        for tr in table.select("tr"):
            cells = [td.get_text(strip=True) for td in tr.select("td")]
            if cells and headers:
                rows.append(dict(zip(headers, cells)))
        return rows

    def __repr__(self) -> str:
        title = self.find_text("title") or "untitled"
        return f"HtmlParser(title={title!r})"


class JsonParser:
    """
    Parse and extract fields from JSON/dict data.

    Usage:
        parser = JsonParser(data)
        name  = parser.get("user", "name")
        flat  = parser.flatten()
    """

    def __init__(self, data: Any):
        if data is None:
            raise ParserError("Data cannot be None.")
        self._data = data

    def get(self, *keys, default=None) -> Any:
        result = self._data
        for key in keys:
            try:
                result = result[key]
            except (KeyError, IndexError, TypeError):
                return default
        return result

    def flatten(self, sep: str = ".") -> Dict[str, Any]:
        def _flatten(obj, prefix=""):
            items = {}
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{prefix}{sep}{k}" if prefix else k
                    items.update(_flatten(v, new_key))
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    new_key = f"{prefix}{sep}{i}" if prefix else str(i)
                    items.update(_flatten(v, new_key))
            else:
                items[prefix] = obj
            return items
        return _flatten(self._data)

    def keys(self) -> List[str]:
        return list(self._data.keys()) if isinstance(self._data, dict) else []

    def __repr__(self) -> str:
        return f"JsonParser(type={type(self._data).__name__})"
