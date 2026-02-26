"""
Data cleaner.
"""
from typing import List, Dict, Any, Optional
from ..utils import clean_whitespace, is_empty, to_str


class DataCleanerError(Exception):
    pass


class DataCleaner:
    """
    Clean and normalize a list of dicts using method chaining.

    Usage:
        result = (
            DataCleaner(rows)
            .drop_nulls(["name"])
            .drop_duplicates(["id"])
            .strip_whitespace()
            .to_list()
        )
    """

    def __init__(self, data: List[Dict[str, Any]]):
        if not isinstance(data, list):
            raise DataCleanerError("Data must be a list of dicts.")
        self._data = [row.copy() for row in data]
        self._original_count = len(data)

    @property
    def count(self) -> int:
        return len(self._data)

    @property
    def columns(self) -> List[str]:
        return list(self._data[0].keys()) if self._data else []

    def drop_nulls(self, columns: Optional[List[str]] = None) -> "DataCleaner":
        def is_valid(row):
            cols = columns or row.keys()
            return all(not is_empty(to_str(row.get(c, ""))) for c in cols)
        self._data = [row for row in self._data if is_valid(row)]
        return self

    def drop_duplicates(self, keys: Optional[List[str]] = None) -> "DataCleaner":
        seen = set()
        result = []
        for row in self._data:
            identifier = tuple(row.get(k) for k in keys) if keys else tuple(sorted(row.items()))
            if identifier not in seen:
                seen.add(identifier)
                result.append(row)
        self._data = result
        return self

    def strip_whitespace(self, columns: Optional[List[str]] = None) -> "DataCleaner":
        for row in self._data:
            cols = columns or list(row.keys())
            for col in cols:
                if isinstance(row.get(col), str):
                    row[col] = clean_whitespace(row[col])
        return self

    def rename_columns(self, mapping: Dict[str, str]) -> "DataCleaner":
        self._data = [{mapping.get(k, k): v for k, v in row.items()} for row in self._data]
        return self

    def select_columns(self, columns: List[str]) -> "DataCleaner":
        self._data = [{k: row.get(k) for k in columns} for row in self._data]
        return self

    def fill_null(self, value: Any = "", columns: Optional[List[str]] = None) -> "DataCleaner":
        for row in self._data:
            cols = columns or list(row.keys())
            for col in cols:
                if is_empty(to_str(row.get(col, ""))):
                    row[col] = value
        return self

    def to_list(self) -> List[Dict[str, Any]]:
        return self._data

    def summary(self) -> Dict[str, Any]:
        return {
            "original_count": self._original_count,
            "cleaned_count": self.count,
            "dropped": self._original_count - self.count,
            "columns": self.columns,
        }

    def __len__(self) -> int:
        return self.count

    def __repr__(self) -> str:
        return f"DataCleaner(rows={self.count}, columns={self.columns})"
