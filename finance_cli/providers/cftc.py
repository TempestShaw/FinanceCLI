"""CFTC Commitments of Traders, using the official futures-only datasets."""
from __future__ import annotations

from datetime import datetime
import math
import re
from typing import Any

import httpx

from finance_cli.core.common import utc_now
from finance_cli.providers.base import ProviderError


DATASETS = {"disaggregated": "72hh-3qpy", "tff": "gpe5-46if", "legacy": "6dca-aqww"}
MARKETS = {"gold": "088691", "sp500": "13874A"}
# Field names are the API's names, including its historical underscores/typos.
CATEGORIES = {
    "disaggregated": {
        "producer_merchant": ("prod_merc_positions_long", "prod_merc_positions_short", None),
        "swap_dealer": ("swap_positions_long_all", "swap__positions_short_all", "swap__positions_spread_all"),
        "managed_money": ("m_money_positions_long_all", "m_money_positions_short_all", "m_money_positions_spread"),
        "other_reportable": ("other_rept_positions_long", "other_rept_positions_short", "other_rept_positions_spread"),
    },
    "tff": {
        "dealer_intermediary": ("dealer_positions_long_all", "dealer_positions_short_all", "dealer_positions_spread_all"),
        "asset_manager": ("asset_mgr_positions_long", "asset_mgr_positions_short", "asset_mgr_positions_spread"),
        "leveraged_money": ("lev_money_positions_long", "lev_money_positions_short", "lev_money_positions_spread"),
        "other_reportable": ("other_rept_positions_long", "other_rept_positions_short", "other_rept_positions_spread"),
    },
    "legacy": {
        "noncommercial": ("noncomm_positions_long_all", "noncomm_positions_short_all", "noncomm_postions_spread_all"),
        "commercial": ("comm_positions_long_all", "comm_positions_short_all", None),
    },
}


class CFTCProvider:
    BASE_URL = "https://publicreporting.cftc.gov"

    def __init__(self, *, timeout: float = 20.0) -> None:
        self.timeout = timeout

    def cot(self, market: str = "gold", *, report: str = "disaggregated", weeks: int = 52) -> dict[str, Any]:
        report = report.strip().lower()
        if report not in DATASETS:
            raise ProviderError("report must be disaggregated, tff or legacy")
        if not 1 <= weeks <= 1000:
            raise ProviderError("weeks must be between 1 and 1000")
        code = MARKETS.get(market.strip().lower(), market.strip().upper())
        if not re.fullmatch(r"[0-9A-Z]{6}", code):
            raise ProviderError("market must be gold, sp500 or a six-character CFTC contract market code")
        dataset = DATASETS[report]
        endpoint = f"{self.BASE_URL}/resource/{dataset}.json"
        categories = {**CATEGORIES[report],
                      "nonreportable": ("nonrept_positions_long_all", "nonrept_positions_short_all", None)}
        fields = ["market_and_exchange_names", "cftc_contract_market_code", "report_date_as_yyyy_mm_dd",
                  "open_interest_all", "contract_units"]
        fields.extend(field for columns in categories.values() for field in columns if field)
        try:
            response = httpx.get(endpoint, params={
                "cftc_contract_market_code": code, "$limit": weeks,
                "$order": "report_date_as_yyyy_mm_dd DESC", "$select": ",".join(fields),
            }, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"CFTC request failed (HTTP {exc.response.status_code})") from None
        except (httpx.RequestError, ValueError):
            raise ProviderError("CFTC request failed or returned invalid JSON") from None
        if not isinstance(payload, list) or any(not isinstance(row, dict) for row in payload):
            raise ProviderError("CFTC returned an unexpected report payload")
        rows = []
        source_url = f"{self.BASE_URL}/d/{dataset}"
        for row in payload:
            if (any(field not in row for field in fields)
                    or row.get("cftc_contract_market_code") != code
                    or not isinstance(row.get("market_and_exchange_names"), str)
                    or not row["market_and_exchange_names"].strip()):
                raise ProviderError("CFTC report is missing requested fields or has a different contract identity")
            try:
                report_date = row["report_date_as_yyyy_mm_dd"]
                if not isinstance(report_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?", report_date):
                    raise ValueError("invalid position date")
                as_of_date = datetime.fromisoformat(report_date).date().isoformat()
            except ValueError:
                raise ProviderError("CFTC returned an invalid position date") from None
            for category, (long_field, short_field, spread_field) in categories.items():
                long = _integer(row.get(long_field))
                short = _integer(row.get(short_field))
                rows.append({
                    "market": row.get("market_and_exchange_names"), "contract_market_code": code,
                    "period": as_of_date, "as_of_date": as_of_date, "category": category,
                    "long": long, "short": short,
                    "net": long - short if long is not None and short is not None else None,
                    "spreading": _integer(row.get(spread_field)) if spread_field else None,
                    "open_interest": _integer(row.get("open_interest_all")),
                    "units": "contracts", "contract_units": row.get("contract_units"),
                    "report": report, "futures_only": True, "source_url": source_url,
                })
        warnings = [] if rows else ["No reports matched this contract in the selected report family."]
        return {"entity": code, "market": market, "contract_market_code": code, "report": report,
                "futures_only": True, "weeks_requested": weeks, "weeks_returned": len(payload),
                "rows": rows, "count": len(rows), "source": "cftc", "source_url": source_url,
                "retrieved_at": utc_now(), "warnings": warnings,
                "notes": ["as_of_date is the position date, not the publication date. Exact publication timestamps are not supplied by this dataset.",
                          "Net equals long minus short within each report category; report families use different trader classifications."]}


def _integer(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        if isinstance(value, bool):
            raise ValueError("invalid contract count")
        number = float(value)
        if not math.isfinite(number) or not number.is_integer() or number < 0:
            raise ValueError("invalid contract count")
        return int(number)
    except (ValueError, TypeError):
        raise ProviderError("CFTC returned an invalid contract count") from None
