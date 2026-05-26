"""Shared global CLI option metadata."""
from __future__ import annotations

OUTPUT_FORMATS = ("json", "text", "compact", "schema")

GLOBAL_OPTIONS = {
    "--output": list(OUTPUT_FORMATS),
    "--fields": [],
    "--max-records": [],
    "--max-chars": [],
    "--list": [],
    "--help": [],
}
