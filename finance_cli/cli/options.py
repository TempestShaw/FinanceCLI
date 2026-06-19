"""Shared global CLI option metadata."""
from __future__ import annotations

OUTPUT_FORMATS = ("json", "md", "text", "compact", "schema", "table", "report", "pretty-json")

GLOBAL_OPTIONS = {
    "--output": list(OUTPUT_FORMATS),
    "--fields": [],
    "--max-records": [],
    "--max-chars": [],
    "--list": [],
    "--help": [],
}
