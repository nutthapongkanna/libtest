"""
Data type converter.
"""
from typing import List, Dict, Any
from ..utils import to_int, to_float, to_bool, to_str, to_iso


class DataConverterError(Exception):
    pass


class DataConverter:
    """
    Convert column types using method chaining.

    Usage:
        result = (
            DataConverter(rows)
            .cast({"age": "int", "price": "float", "date": "date"})
            .to_list()
        )
    """

    def __init__(self, data: List[Dict[str, Any]]):
        if not isinstance(data, list):
            raise DataConverterError("Data must be a list of dicts.")
        self._data = [row.copy() for row in data]

    @property
    def count(self) -> int:
        return len(self._data)

    @property
    def columns(self) -> List[str]:
        return list(self._data[0].keys()) if self._data else []

    def to_int(self, columns: List[str]) -> "DataConverter":
        for row in self._data:
            for col in columns:
                if col in row:
                    row[col] = to_int(row[col])
        return self

    def to_float(self, columns: List[str]) -> "DataConverter":
        for row in self._data:
            for col in columns:
                if col in row:
                    row[col] = to_float(row[col])
        return self

    def to_bool(self, columns: List[str]) -> "DataConverter":
        for row in self._data:
            for col in columns:
                if col in row:
                    row[col] = to_bool(row[col])
        return self

    def to_str(self, columns: List[str]) -> "DataConverter":
        for row in self._data:
            for col in columns:
                if col in row:
                    row[col] = to_str(row[col])
        return self

    def to_date_iso(self, columns: List[str]) -> "DataConverter":
        for row in self._data:
            for col in columns:
                if col in row:
                    row[col] = to_iso(to_str(row[col]))
        return self

    def cast(self, schema: Dict[str, str]) -> "DataConverter":
        """Cast multiple columns at once using schema dict."""
        type_map = {
            "int":   lambda cols: self.to_int(cols),
            "float": lambda cols: self.to_float(cols),
            "bool":  lambda cols: self.to_bool(cols),
            "str":   lambda cols: self.to_str(cols),
            "date":  lambda cols: self.to_date_iso(cols),
        }
        grouped: Dict[str, List[str]] = {}
        for col, dtype in schema.items():
            grouped.setdefault(dtype, []).append(col)
        for dtype, cols in grouped.items():
            if dtype not in type_map:
                raise DataConverterError(f"Unknown type: {dtype!r}. Use: {list(type_map.keys())}")
            type_map[dtype](cols)
        return self

    def to_list(self) -> List[Dict[str, Any]]:
        return self._data

    def __len__(self) -> int:
        return self.count

    def __repr__(self) -> str:
        return f"DataConverter(rows={self.count}, columns={self.columns})"
