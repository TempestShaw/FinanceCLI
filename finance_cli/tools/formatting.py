"""Formatting helpers for finance LLM tools."""
from __future__ import annotations

import json
from typing import Any


def as_tool_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str, allow_nan=False)
