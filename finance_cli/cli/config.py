"""User configuration for FinanceCLI command-line behavior."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib


VALID_OUTPUT_FORMATS = ("json", "md", "text", "compact", "schema", "table", "report", "pretty-json")


def config_path() -> Path:
    configured = os.getenv("FINANCECLI_CONFIG")
    if configured:
        return Path(configured).expanduser()
    config_home = os.getenv("XDG_CONFIG_HOME")
    base = Path(config_home).expanduser() if config_home else Path.home() / ".config"
    return base / "finance-cli" / "config.toml"


def load_config(path: Path | None = None) -> dict[str, Any]:
    target = path or config_path()
    if not target.exists():
        return {}
    return tomllib.loads(target.read_text(encoding="utf-8"))


def resolve_output_format(
    explicit_output: str | None,
    *,
    is_interactive: bool,
    path: Path | None = None,
) -> str:
    if explicit_output:
        return _validated_output(explicit_output)
    env_output = os.getenv("FINANCECLI_OUTPUT")
    if env_output:
        return _validated_output(env_output)

    output_config = load_config(path).get("output")
    output = output_config if isinstance(output_config, dict) else {}
    if not is_interactive and output.get("non_interactive_default"):
        return _validated_output(str(output["non_interactive_default"]))
    if output.get("default"):
        return _validated_output(str(output["default"]))
    return "json"


def set_config_value(key: str, value: str, *, path: Path | None = None) -> dict[str, Any]:
    parts = _split_key(key)
    target = path or config_path()
    config = load_config(target)
    section = config.setdefault(parts[0], {})
    if not isinstance(section, dict):
        raise ValueError(f"cannot set nested key under non-table config value: {parts[0]}")
    parsed = _parse_value(value)
    if parts[0] == "output" and parts[1] in {"default", "non_interactive_default"}:
        parsed = _validated_output(str(parsed))
    section[parts[1]] = parsed
    _write_config(target, config)
    return {"path": str(target), "key": key, "value": section[parts[1]]}


def unset_config_value(key: str, *, path: Path | None = None) -> dict[str, Any]:
    parts = _split_key(key)
    target = path or config_path()
    config = load_config(target)
    section = config.get(parts[0])
    removed = False
    if isinstance(section, dict) and parts[1] in section:
        del section[parts[1]]
        removed = True
    _write_config(target, config)
    return {"path": str(target), "key": key, "removed": removed}


def _validated_output(value: str) -> str:
    if value not in VALID_OUTPUT_FORMATS:
        allowed = ", ".join(VALID_OUTPUT_FORMATS)
        raise ValueError(f"unknown output format: {value}. Use one of: {allowed}")
    return value


def _split_key(key: str) -> tuple[str, str]:
    parts = key.split(".")
    if len(parts) != 2 or not all(parts):
        raise ValueError("config key must use section.name form, for example output.default")
    return parts[0], parts[1]


def _parse_value(value: str) -> Any:
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value


def _write_config(path: Path, config: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for section_name, section in config.items():
        if not isinstance(section, dict):
            continue
        lines.append(f"[{section_name}]")
        for key, value in section.items():
            lines.append(f"{key} = {_toml_value(value)}")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
