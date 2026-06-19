"""Fundamental data services."""
from __future__ import annotations

import re
from typing import Any

from finance_cli.providers.sec_edgar import SecEdgarProvider
from finance_cli.providers.yahoo import YahooFinanceProvider


def fetch_financial_statement(
    symbol: str,
    *,
    statement: str = "income",
    period: str = "annual",
    provider: str | SecEdgarProvider | YahooFinanceProvider | None = "sec",
) -> dict[str, Any]:
    """Fetch a normalized financial statement table."""
    if provider is None:
        provider = "sec"
    if isinstance(provider, str):
        provider_key = provider.strip().lower()
        if provider_key == "sec":
            client = SecEdgarProvider()
        elif provider_key == "yahoo":
            client = YahooFinanceProvider()
        else:
            raise ValueError("provider must be sec or yahoo")
    else:
        client = provider
    return client.financial_statement(symbol, statement=statement, period=period)


def fetch_financial_statement_with_display(
    symbol: str,
    *,
    statement: str = "income",
    period: str = "annual",
    provider: str | SecEdgarProvider | YahooFinanceProvider | None = "sec",
) -> tuple[dict[str, Any], Any | None]:
    """Fetch a financial statement plus provider-native display when available."""
    if provider is None:
        provider = "sec"
    if isinstance(provider, str):
        provider_key = provider.strip().lower()
        if provider_key == "sec":
            client = SecEdgarProvider()
        elif provider_key == "yahoo":
            data = YahooFinanceProvider().financial_statement(symbol, statement=statement, period=period)
            return data, None
        else:
            raise ValueError("provider must be sec or yahoo")
    else:
        client = provider
    if hasattr(client, "financial_statement_with_display"):
        return client.financial_statement_with_display(symbol, statement=statement, period=period)
    return client.financial_statement(symbol, statement=statement, period=period), None


def fetch_financial_metrics(
    symbol: str,
    *,
    period: str = "quarterly",
    metrics: list[str] | None = None,
    provider: SecEdgarProvider | None = None,
) -> dict[str, Any]:
    """Fetch standard financial metrics using SEC/edgartools financial getters."""
    client = provider or SecEdgarProvider()
    return client.financial_metrics(symbol, period=period, metrics=metrics)


def fundamentals_growth(
    symbol: str,
    *,
    metrics: list[str] | None = None,
    periods: list[str] | None = None,
    years: int = 5,
    provider: str | SecEdgarProvider | YahooFinanceProvider | None = "sec",
) -> dict[str, Any]:
    """Return raw fundamental history plus deterministic growth calculations."""
    normalized_symbol = symbol.strip().upper()
    metric_keys = [_normalize_metric(metric) for metric in (metrics or ["revenue", "eps", "operating_margin", "net_margin", "roe"])]
    period_keys = [period.strip().lower() for period in (periods or ["quarterly", "annual"]) if period.strip()]
    client = _statement_provider(provider)
    output_rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    sources: list[str] = []
    requested_years = max(1, int(years))

    for period_type in period_keys:
        payload = client.financial_statement(normalized_symbol, statement="income", period=period_type)
        rows = _normalized_fundamental_rows(
            payload.get("rows") or [],
            metrics=metric_keys,
            period_type=period_type,
            periods=payload.get("periods") or [],
        )
        source = payload.get("source")
        if payload.get("source"):
            sources.append(str(payload["source"]))
        if period_type == "annual":
            if rows and len(rows) < requested_years:
                warnings.append(f"requested {requested_years} annual years but only {len(rows)} annual rows are available")
            rows = rows[-requested_years:]
        if period_type == "quarterly" and rows and _latest_quarter_pair(rows) is None:
            warnings.append("quarterly same-quarter prior-year comparison unavailable")
        for row in rows:
            for metric in metric_keys:
                value = row["values"].get(metric)
                if value is None:
                    continue
                output_rows.append({
                    "kind": "history",
                    "symbol": normalized_symbol,
                    "metric": metric,
                    "period_type": period_type,
                    "period": row["period"],
                    "value": value,
                    "method": row["methods"].get(metric),
                    "source": source,
                })
        output_rows.extend(_growth_rows(normalized_symbol, metric_keys, period_type, rows, source=source))

        if not rows:
            warnings.append(f"{period_type} income statement rows unavailable")

    return {
        "symbol": normalized_symbol,
        "rows": output_rows,
        "count": len(output_rows),
        "warnings": warnings,
        "source": ",".join(dict.fromkeys(sources)) if sources else None,
    }


def _statement_provider(provider: str | SecEdgarProvider | YahooFinanceProvider | None) -> SecEdgarProvider | YahooFinanceProvider:
    if provider is None:
        return SecEdgarProvider()
    if isinstance(provider, str):
        provider_key = provider.strip().lower()
        if provider_key == "sec":
            return SecEdgarProvider()
        if provider_key == "yahoo":
            return YahooFinanceProvider()
        raise ValueError("provider must be sec or yahoo")
    return provider


def _normalized_fundamental_rows(
    rows: list[dict[str, Any]],
    *,
    metrics: list[str],
    period_type: str,
    periods: list[Any] | None = None,
) -> list[dict[str, Any]]:
    rows = _statement_period_rows(rows, periods=periods) or rows
    normalized = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        period = _period_label(row, fallback=str(index + 1))
        values: dict[str, float | None] = {}
        methods: dict[str, str | None] = {}
        for metric in metrics:
            value, method = _metric_value(row, metric)
            values[metric] = value
            methods[metric] = method
        sort_key = _period_sort_key(period, period_type)
        normalized.append({"period": period, "values": values, "methods": methods, "sort_key": sort_key})
    return sorted(normalized, key=lambda item: item["sort_key"])


def _statement_period_rows(rows: list[dict[str, Any]], *, periods: list[Any] | None) -> list[dict[str, Any]]:
    period_columns = _statement_period_columns(rows, periods=periods)
    if not period_columns:
        return []
    metric_rows = _statement_metric_rows(rows)
    if not metric_rows:
        return []

    output: list[dict[str, Any]] = []
    for period in period_columns:
        row: dict[str, Any] = {"period": period}
        for metric, source_row in metric_rows.items():
            value = _number(source_row.get(period))
            if value is not None:
                row[metric] = value
        output.append(row)
    return output


def _statement_period_columns(rows: list[dict[str, Any]], *, periods: list[Any] | None) -> list[str]:
    if any(_has_explicit_period_row(row) for row in rows if isinstance(row, dict)):
        return []
    if periods:
        candidates = [str(period) for period in periods]
        return [period for period in candidates if any(isinstance(row, dict) and period in row for row in rows)]

    columns: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key, value in row.items():
            if key in {"concept", "label", "unit", "level", "abstract"}:
                continue
            if _number(value) is not None and re.search(r"\d{4}", str(key)) and key not in columns:
                columns.append(str(key))
    return columns


def _has_explicit_period_row(row: dict[str, Any]) -> bool:
    return any(row.get(key) not in (None, "") for key in ("period", "fiscal_period", "date", "end_date", "as_of_date"))


def _statement_metric_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    metric_rows: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        metric = _statement_metric(row)
        if metric and metric not in metric_rows:
            metric_rows[metric] = row
    return metric_rows


def _statement_metric(row: dict[str, Any]) -> str | None:
    concept = str(row.get("concept") or "")
    label = str(row.get("label") or "")
    text = f"{concept} {label}".lower()
    compact = re.sub(r"[^a-z0-9]", "", text)
    label_text = label.strip().lower()

    if "weightedaveragenumberofdilutedsharesoutstanding" in compact:
        return "diluted_shares"
    if "earningspersharediluted" in compact or "dilutedeps" in compact:
        return "diluted_eps"
    if "operatingincomeloss" in compact or label_text in {"operating income", "operating income loss"}:
        return "operating_income"
    if "netincomeloss" in compact or label_text in {"net income", "net income loss"}:
        return "net_income"
    if "stockholdersequity" in compact or label_text in {"stockholders equity", "shareholders equity"}:
        return "stockholders_equity"
    if _is_revenue_statement_row(compact, label_text):
        return "revenue"
    return None


def _is_revenue_statement_row(compact: str, label_text: str) -> bool:
    if label_text in {"revenue", "revenues", "net sales", "sales"}:
        return True
    if "costofrevenue" in compact or "deferredrevenue" in compact:
        return False
    return "usgaaprevenues" in compact or compact.endswith("revenues")


def _growth_rows(
    symbol: str,
    metrics: list[str],
    period_type: str,
    rows: list[dict[str, Any]],
    *,
    source: Any,
) -> list[dict[str, Any]]:
    growth: list[dict[str, Any]] = []
    for metric in metrics:
        if period_type == "quarterly":
            pair = _latest_quarter_pair(rows)
            if pair is None:
                continue
            previous, current = pair
            growth.extend(_comparison_rows(symbol, metric, period_type, previous, current, growth_type="yoy", source=source))
        elif period_type == "annual":
            for previous, current in zip(rows, rows[1:]):
                growth.extend(_comparison_rows(symbol, metric, period_type, previous, current, growth_type="yoy", source=source))
            cagr = _cagr_row(symbol, metric, period_type, rows, source=source)
            if cagr:
                growth.append(cagr)
    return growth


def _comparison_rows(
    symbol: str,
    metric: str,
    period_type: str,
    previous: dict[str, Any],
    current: dict[str, Any],
    *,
    growth_type: str,
    source: Any,
) -> list[dict[str, Any]]:
    previous_value = previous["values"].get(metric)
    current_value = current["values"].get(metric)
    if previous_value is None or current_value is None:
        return []
    row_type = "delta" if metric in {"operating_margin", "net_margin", "roe"} else "growth"
    row = {
        "kind": row_type,
        "symbol": symbol,
        "metric": metric,
        "period_type": period_type,
        "current_period": current["period"],
        "comparison_period": previous["period"],
        "current_value": current_value,
        "comparison_value": previous_value,
        "growth_type": growth_type,
        "growth_pct": _growth_pct(current_value, previous_value) if row_type == "growth" else None,
        "delta": _round_number(current_value - previous_value) if row_type == "delta" else None,
        "method": current["methods"].get(metric),
        "source": source,
    }
    return [row]


def _cagr_row(symbol: str, metric: str, period_type: str, rows: list[dict[str, Any]], *, source: Any) -> dict[str, Any] | None:
    if metric in {"operating_margin", "net_margin", "roe"} or len(rows) < 2:
        return None
    start = rows[0]
    end = rows[-1]
    start_value = start["values"].get(metric)
    end_value = end["values"].get(metric)
    if start_value is None or end_value is None or start_value <= 0 or end_value <= 0:
        return None
    years = max(1, len(rows) - 1)
    return {
        "kind": "growth",
        "symbol": symbol,
        "metric": metric,
        "period_type": period_type,
        "start_period": start["period"],
        "end_period": end["period"],
        "start_value": start_value,
        "end_value": end_value,
        "growth_type": "cagr",
        "years": years,
        "growth_pct": _round_number(((end_value / start_value) ** (1 / years) - 1) * 100),
        "method": end["methods"].get(metric),
        "source": source,
    }


def _latest_quarter_pair(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]] | None:
    if len(rows) < 2:
        return None
    latest = rows[-1]
    latest_quarter = _quarter_number(latest["period"])
    latest_year = _period_year(latest["period"])
    if latest_quarter is None or latest_year is None:
        return None
    candidates = [
        row for row in rows[:-1]
        if _quarter_number(row["period"]) == latest_quarter and _period_year(row["period"]) == latest_year - 1
    ]
    if candidates:
        return candidates[-1], latest
    return None


def _metric_value(row: dict[str, Any], metric: str) -> tuple[float | None, str | None]:
    if metric == "revenue":
        return _first_number(row, ("revenue", "total_revenue", "Total Revenue", "Revenues")), "statement"
    if metric == "eps":
        reported = _first_number(row, ("diluted_eps", "eps_diluted", "Diluted EPS", "Diluted EPS Excluding ExtraOrd Items"))
        if reported is not None:
            return reported, "reported_diluted_eps"
        net_income = _first_number(row, ("net_income", "Net Income", "Net Income Common Stockholders"))
        shares = _first_number(row, ("diluted_shares", "shares_diluted", "Diluted Average Shares", "diluted_average_shares"))
        return _safe_ratio(net_income, shares), "net_income / diluted_shares"
    if metric == "operating_margin":
        direct = _first_number(row, ("operating_margin", "operating_margins"))
        if direct is not None:
            return direct, "statement"
        return _safe_ratio(_first_number(row, ("operating_income", "Operating Income")), _first_number(row, ("revenue", "total_revenue", "Total Revenue", "Revenues"))), "operating_income / revenue"
    if metric == "net_margin":
        direct = _first_number(row, ("net_margin", "profit_margin", "profit_margins"))
        if direct is not None:
            return direct, "statement"
        return _safe_ratio(_first_number(row, ("net_income", "Net Income", "Net Income Common Stockholders")), _first_number(row, ("revenue", "total_revenue", "Total Revenue", "Revenues"))), "net_income / revenue"
    if metric == "roe":
        direct = _first_number(row, ("roe", "return_on_equity"))
        if direct is not None:
            return direct, "statement"
        return _safe_ratio(_first_number(row, ("net_income", "Net Income", "Net Income Common Stockholders")), _first_number(row, ("stockholders_equity", "Stockholders Equity"))), "net_income / stockholders_equity"
    return _first_number(row, (metric,)), "statement"


def _period_label(row: dict[str, Any], *, fallback: str) -> str:
    for key in ("period", "fiscal_period", "date", "end_date", "as_of_date"):
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return fallback


def _period_sort_key(period: str, period_type: str) -> tuple[int, int, str]:
    match = re.search(r"(\d{4}).*?Q([1-4])", period, flags=re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2)), period
    year_match = re.search(r"(\d{4})", period)
    year = int(year_match.group(1)) if year_match else 0
    return year, 4 if period_type == "annual" else 0, period


def _quarter_number(period: str) -> int | None:
    match = re.search(r"Q([1-4])", period, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _period_year(period: str) -> int | None:
    match = re.search(r"(\d{4})", period)
    return int(match.group(1)) if match else None


def _normalize_metric(metric: str) -> str:
    normalized = str(metric).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "sales": "revenue",
        "total_revenue": "revenue",
        "diluted_eps": "eps",
        "profit_margin": "net_margin",
        "return_on_equity": "roe",
    }
    return aliases.get(normalized, normalized)


def _first_number(row: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        value = row.get(key)
        number = _number(value)
        if number is not None:
            return number
    return None


def _number(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _safe_ratio(numerator: Any, denominator: Any) -> float | None:
    top = _number(numerator)
    bottom = _number(denominator)
    if top is None or bottom in (None, 0):
        return None
    return top / bottom


def _growth_pct(current_value: float, previous_value: float) -> float | None:
    if previous_value == 0:
        return None
    return _round_number(((current_value / previous_value) - 1) * 100)


def _round_number(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 4)
