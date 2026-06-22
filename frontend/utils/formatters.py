from __future__ import annotations

from typing import Any


def format_datetime(value: Any) -> str:
    if not value:
        return "-"
    return str(value).replace("T", " ")


def safe_number(value: Any, fallback: str = "N/A") -> Any:
    return fallback if value is None else value


def trim_source_name(source: str) -> str:
    if not source:
        return "-"
    return source.split("/")[-1]


def has_meaningful_values(values: list[Any]) -> bool:
    cleaned = [v for v in values if v is not None]
    return len(cleaned) > 0