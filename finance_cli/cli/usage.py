"""Parse FinanceCommand usage strings for docs and shell completion."""
from __future__ import annotations

import re
import shlex
from typing import Any


def parse_usage_params(usage: str) -> dict[str, dict[str, Any]]:
    if not usage:
        return {}
    parts = _split_usage(usage)
    tokens = parts[1:]
    params: dict[str, dict[str, Any]] = {}
    for token, optional in tokens:
        for raw_part in _expand_token(token):
            parsed = _parse_token(raw_part, optional=optional)
            if parsed is None:
                continue
            name, meta = parsed
            if name in params:
                params[name] = {**params[name], **meta}
                params[name]["required"] = params[name].get("required", False) or meta.get("required", False)
            else:
                params[name] = meta
    return params


def _split_usage(usage: str) -> list[tuple[str, bool]]:
    tokens: list[tuple[str, bool]] = []
    current: list[str] = []
    optional = False
    for char in usage:
        if char == "[":
            if current:
                tokens.extend((part, optional) for part in _shell_split("".join(current)))
                current = []
            optional = True
            continue
        if char == "]":
            if current:
                tokens.extend((part, True) for part in _shell_split("".join(current)))
                current = []
            optional = False
            continue
        current.append(char)
    if current:
        tokens.extend((part, optional) for part in _shell_split("".join(current)))
    return tokens


def _shell_split(text: str) -> list[str]:
    try:
        return shlex.split(text)
    except ValueError:
        return text.split()


def _expand_token(token: str) -> list[str]:
    token = token.strip(",")
    if not token or token.startswith("(") or token.endswith(")"):
        return []
    if "|" not in token:
        return [token]
    parts = [part for part in token.split("|") if part]
    if all("=" in part for part in parts):
        return parts
    if any("=" in part for part in parts) and "=" not in parts[0]:
        return [token]
    return [token]


def _parse_token(token: str, *, optional: bool) -> tuple[str, dict[str, Any]] | None:
    token = token.strip()
    if not token or token.startswith("-"):
        return None
    if "=" in token:
        raw_name, raw_value = token.split("=", 1)
        raw_aliases = [_clean_alias(part) for part in raw_name.split("|")]
        raw_aliases = [alias for alias in raw_aliases if alias]
        names = [_normalize_param_name(part) for part in raw_aliases]
        names = [name for name in names if name]
        if not names:
            return None
        meta = _infer_schema_from_value(raw_value)
        meta["required"] = not optional
        if len(raw_aliases) > 1:
            meta["aliases"] = raw_aliases[:-1]
        if not optional:
            meta.pop("default", None)
        if optional and not _is_placeholder_value(raw_value) and "default" not in meta and "|" not in raw_value:
            meta["default"] = _coerce_default(raw_value)
        return names[-1], meta
    name = _normalize_param_name(token)
    if not name:
        return None
    return name, {"type": "string", "required": not optional}


def _normalize_param_name(name: str) -> str:
    name = _clean_alias(name)
    if not name:
        return ""
    if name == "SYMBOL[,SYMBOL...]":
        return "symbols"
    name = name.replace("PATH_OR_URL", "source")
    name = re.sub(r"[^A-Za-z0-9_]+", "_", name).strip("_")
    return name.lower()


def _clean_alias(name: str) -> str:
    return name.strip("<>[]'\"")


def _is_placeholder_value(value: str) -> bool:
    return value == "..." or bool(re.fullmatch(r"[A-Z][A-Z0-9_]*", value))


def _infer_schema_from_value(raw_value: str) -> dict[str, Any]:
    value = raw_value.strip("'\"")
    if "|" in value and not value.startswith("{"):
        enum = [_coerce_default(part) for part in value.split("|") if part and part != "..."]
        return {"type": _common_type_for_enum(enum), "enum": enum}
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return {"type": "boolean", "default": lowered == "true"}
    if re.fullmatch(r"-?\d+", value):
        return {"type": "integer", "default": int(value)}
    if re.fullmatch(r"-?\d+\.\d+", value):
        return {"type": "number", "default": float(value)}
    if value == "YYYY-MM-DD":
        return {"type": "string", "format": "date"}
    if value in {"{}", "'{}'"}:
        return {"type": "object"}
    return {"type": "string"}


def _coerce_default(value: str) -> Any:
    value = value.strip("'\"")
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def _common_type_for_enum(enum: list[Any]) -> str:
    if enum and all(isinstance(item, bool) for item in enum):
        return "boolean"
    if enum and all(isinstance(item, int) for item in enum):
        return "integer"
    if enum and all(isinstance(item, (int, float)) for item in enum):
        return "number"
    return "string"
