"""Common helpers for finance core modules."""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper()
    if not cleaned:
        raise ValueError("symbol is required")
    return cleaned


def parse_scaled_number(value: float | int | str) -> float:
    """Parse numeric CLI inputs such as 2200000000, 2.2B, or 2200M."""
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)([kKmMbBtT])?", text)
    if not match:
        raise ValueError(f"invalid number: {value}")
    number = float(match.group(1))
    suffix = (match.group(2) or "").lower()
    multipliers = {
        "": 1.0,
        "k": 1_000.0,
        "m": 1_000_000.0,
        "b": 1_000_000_000.0,
        "t": 1_000_000_000_000.0,
    }
    return number * multipliers[suffix]


def parse_rate(value: float | int | str | None, warnings: list[str] | None = None) -> float:
    """
    Parse a rate/percentage into a decimal (e.g., 0.08 for 8%).
    Handles "8%", 8, and 0.08.
    If a value > 1 is provided without a % sign, it is treated as a percentage
    (divided by 100) and a warning is added to the warnings list.
    """
    if value is None:
        raise ValueError("rate is required")
    
    rate: float
    is_explicit_pct = False
    
    if isinstance(value, (int, float)):
        rate = float(value)
    else:
        text = str(value).strip()
        if text.endswith("%"):
            rate = float(text[:-1]) / 100.0
            is_explicit_pct = True
        else:
            rate = float(text)
            
    if rate <= -1:
        raise ValueError("rate must be greater than -1")
        
    if not is_explicit_pct and abs(rate) > 1.0:
        rate = rate / 100.0
        if warnings is not None:
            warnings.append(f"Input '{value}' treated as {rate*100:.1f}% (divided by 100)")
            
    return rate


def parse_window(value: str | int, mode: str = "trading") -> int:
    """
    Parse a window string like '1d', '3d', '1w', '1m' into an integer.
    In 'trading' mode: 1w = 5 days, 1m = 21 days.
    In 'calendar' mode: 1w = 7 days, 1m = 30 days.
    """
    if isinstance(value, int):
        return value
        
    normalized = str(value).strip().lower()
    if not normalized:
        return 1
        
    if normalized.isdigit():
        return int(normalized)
        
    index = 0
    while index < len(normalized) and (normalized[index].isdigit() or normalized[index] == "."):
        index += 1
        
    if index == 0:
        raise ValueError(f"invalid window: {value}")
        
    amount = float(normalized[:index])
    unit = normalized[index:] or "d"
    
    if mode == "trading":
        multipliers = {
            "d": 1, "day": 1, "days": 1,
            "w": 5, "wk": 5, "week": 5, "weeks": 5,
            "m": 21, "mo": 21, "month": 21, "months": 21,
        }
    else:
        multipliers = {
            "d": 1, "day": 1, "days": 1,
            "w": 7, "wk": 7, "week": 7, "weeks": 7,
            "m": 30, "mo": 30, "month": 30, "months": 30,
        }
        
    if unit not in multipliers:
        raise ValueError(f"unknown window unit: {unit}")
        
    return int(amount * multipliers[unit])


def parse_date(value: Any) -> date | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    candidates = [
        text[:10],
        text.replace("Z", "+00:00"),
    ]
    # Handle YYYYMMDD
    if len(text) == 8 and text.isdigit():
        candidates.append(f"{text[:4]}-{text[4:6]}-{text[6:8]}")
    compact_datetime = re.fullmatch(
        r"(\d{4})(\d{2})(\d{2})T(?:[01]\d|2[0-3])(?:[0-5]\d){2}(?:Z|[+-](?:[01]\d|2[0-3]):?[0-5]\d)?",
        text,
    )
    if compact_datetime:
        candidates.append(
            f"{compact_datetime.group(1)}-{compact_datetime.group(2)}-{compact_datetime.group(3)}"
        )
        
    for candidate in candidates:
        try:
            return datetime.fromisoformat(candidate).date()
        except ValueError:
            pass
    return None
