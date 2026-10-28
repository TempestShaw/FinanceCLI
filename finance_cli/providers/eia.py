"""Small, bounded EIA v2 inventory and electricity retail-sales queries."""
from __future__ import annotations

from datetime import date
import math
import os
import re
from typing import Any

import httpx

from finance_cli.core.common import utc_now
from finance_cli.providers.base import ProviderError


INVENTORIES = {
    "crude": ("WCESTUS1", "US", "Commercial crude oil excluding the Strategic Petroleum Reserve"),
    "gasoline": ("WGTSTUS1", "US", "Total motor gasoline ending stocks"),
    "distillate": ("WDISTUS1", "US", "Distillate fuel oil ending stocks"),
    "natural_gas": ("NW2_EPG0_SWO_R48_BCF", "Lower 48 States", "Working gas in underground storage"),
}


class EIAProvider:
    BASE_URL = "https://api.eia.gov/v2"

    def __init__(self, *, api_key: str | None = None, timeout: float = 20.0) -> None:
        self.api_key = api_key or os.getenv("EIA_API_KEY")
        self.timeout = timeout

    def inventory(self, *, product: str = "crude", country: str = "US", limit: int = 20) -> dict[str, Any]:
        product = product.strip().lower()
        country = country.strip().upper()
        if country != "US":
            raise ProviderError("country must be US; this command reads US EIA inventory series")
        if product not in INVENTORIES:
            raise ProviderError("product must be crude, gasoline, distillate or natural_gas")
        series_id, region, description = INVENTORIES[product]
        route = "natural-gas/stor/wkly" if product == "natural_gas" else "petroleum/stoc/wstk"
        payload, raw_rows, warnings = self._request(route, {
            "frequency": "weekly", "data[0]": "value", "facets[series][]": series_id,
        }, limit=limit)
        source_url = ("https://www.eia.gov/dnav/ng/hist/nw2_epg0_swo_r48_bcfw.htm"
                      if product == "natural_gas" else
                      f"https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s={series_id}&f=W")
        rows = []
        for row in raw_rows:
            if (row.get("series") != series_id or "value" not in row
                    or not isinstance(row.get("units"), str) or not row["units"].strip()):
                raise ProviderError("EIA inventory row is missing its value/units or has a different series identity")
            rows.append({"period": _period(row.get("period"), "weekly"), "series_id": series_id, "product": product,
                         "country": country, "region": region, "value": _number(row["value"]),
                         "units": row["units"], "frequency": "weekly", "source_url": source_url})
        return self._result(rows, payload, warnings, entity=series_id, product=product, country=country,
                            region=region, series_id=series_id, description=description,
                            frequency="weekly", source_url=source_url)

    def electricity(self, *, region: str = "TX", frequency: str = "monthly", limit: int = 20) -> dict[str, Any]:
        region = region.strip().upper()
        if not re.fullmatch(r"[A-Z]{2}", region):
            raise ProviderError("region must be a two-letter US state code or US")
        frequency = frequency.strip().lower()
        if frequency not in {"monthly", "annual"}:
            raise ProviderError("frequency must be monthly or annual")
        payload, raw_rows, warnings = self._request("electricity/retail-sales", {
            "frequency": frequency, "data[0]": "sales", "data[1]": "price",
            "facets[stateid][]": region, "facets[sectorid][]": "ALL",
        }, limit=limit)
        source_url = "https://www.eia.gov/electricity/data/browser/"
        rows = []
        for row in raw_rows:
            if (row.get("stateid") != region or row.get("sectorid") != "ALL"
                    or any(key not in row for key in ("sales", "price"))
                    or any(not isinstance(row.get(key), str) or not row[key].strip() for key in ("sales-units", "price-units"))):
                raise ProviderError("EIA electricity row is missing values/units or has a different state/sector identity")
            rows.append({"period": _period(row.get("period"), frequency), "region": row["stateid"],
                         "region_name": row.get("stateDescription"), "sector": row.get("sectorName"),
                         "sales": _number(row["sales"]), "sales_units": row["sales-units"],
                         "price": _number(row["price"]), "price_units": row["price-units"],
                         "frequency": frequency, "source_url": source_url})
        return self._result(rows, payload, warnings, entity=region, region=region, frequency=frequency,
                            description="Electricity retail sales and average price, all sectors",
                            source_url=source_url)

    def _request(self, route: str, params: dict[str, Any], *, limit: int) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
        if not 1 <= limit <= 5000:
            raise ProviderError("limit must be between 1 and 5000")
        if not self.api_key:
            raise ProviderError("EIA API key is required. Set EIA_API_KEY.")
        try:
            response = httpx.get(f"{self.BASE_URL}/{route}/data/", params={
                **params, "api_key": self.api_key, "sort[0][column]": "period",
                "sort[0][direction]": "desc", "offset": 0, "length": limit,
            }, timeout=self.timeout)
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"EIA request failed (HTTP {exc.response.status_code})") from None
        except (httpx.RequestError, ValueError):
            raise ProviderError("EIA request failed or returned invalid JSON") from None
        if not isinstance(body, dict) or body.get("error"):
            raise ProviderError("EIA API returned an error or unexpected payload")
        payload = body.get("response")
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise ProviderError("EIA returned an unexpected data payload")
        if any(not isinstance(row, dict) for row in payload["data"]):
            raise ProviderError("EIA returned an unexpected data row")
        warnings = [str(body[key]).replace(self.api_key, "<redacted>")
                    for key in ("warning", "description") if body.get("warning") and body.get(key)]
        return payload, payload["data"][:limit], warnings

    def _result(self, rows: list[dict[str, Any]], payload: dict[str, Any], warnings: list[str], **context: Any) -> dict[str, Any]:
        total = int(payload.get("total", len(rows)))
        truncated = total > len(rows)
        if truncated:
            warnings.append("Only the latest requested limit is returned; older observations are omitted.")
        return {**context, "rows": rows, "count": len(rows), "source": "eia",
                "retrieved_at": utc_now(), "total_available": total, "truncated": truncated,
                "warnings": warnings}


def _number(value: Any) -> float | None:
    if value in (None, "", "--", "NA", "W", "-", "."):
        return None
    try:
        if isinstance(value, bool):
            raise ValueError("invalid numeric value")
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("non-finite numeric value")
        return number
    except (ValueError, TypeError):
        raise ProviderError("EIA returned an invalid numeric value") from None


def _period(value: Any, frequency: str) -> str:
    patterns = {"weekly": r"\d{4}-\d{2}-\d{2}", "monthly": r"\d{4}-\d{2}", "annual": r"\d{4}"}
    try:
        if not isinstance(value, str) or not re.fullmatch(patterns[frequency], value):
            raise ValueError("invalid period format")
        suffix = "-01-01" if frequency == "annual" else "-01" if frequency == "monthly" else ""
        date.fromisoformat(value + suffix)
    except ValueError:
        raise ProviderError("EIA returned an invalid observation period") from None
    return value
