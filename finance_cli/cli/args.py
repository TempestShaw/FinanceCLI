"""Argument parsing helpers for simple finance CLI commands."""
from __future__ import annotations

import json
from typing import Any


def parse_key_values(args: list[str]) -> dict[str, str]:
    """Parse key=value tokens from a command's trailing args."""
    parsed: dict[str, str] = {}
    for arg in args:
        if "=" not in arg:
            continue
        key, value = arg.split("=", 1)
        if key:
            parsed[key.strip()] = value.strip()
    return parsed


class KVArgs:
    """Small typed accessor for key=value command arguments."""

    def __init__(self, args: list[str]) -> None:
        self.values = parse_key_values(args)

    def str(self, key: str, default: str | None = None) -> str | None:
        return self.values.get(key, default)

    def int(self, key: str, default: int) -> int:
        value = self.values.get(key)
        return int(value) if value is not None else default

    def float(self, key: str, default: float) -> float:
        value = self.values.get(key)
        return float(value) if value is not None else default

    def bool(self, key: str, default: bool = False) -> bool:
        value = self.values.get(key)
        if value is None:
            return default
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}

    def csv(self, key: str) -> list[str]:
        return parse_csv(self.values.get(key))

    def json_object(self, key: str) -> dict[str, Any]:
        return parse_json_object(self.values.get(key))


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_json_object(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    payload = json.loads(value)
    if not isinstance(payload, dict):
        raise ValueError("JSON value must be an object")
    return payload
