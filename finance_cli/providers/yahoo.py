"""Yahoo Finance provider."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
import re
from typing import Any

from finance_cli.providers.base import ProviderError, quiet_call, require_dependency


MARKET_INSTALL_HINT = "Install or repair Finance CLI with: python -m pip install -U finresearch-cli"
MAX_TABLE_ROWS = 100


TIMEFRAME_CONFIGS = {
    "5m": {"interval": "5m", "period": "5d", "max_backfill": "60d"},
    "15m": {"interval": "15m", "period": "5d", "max_backfill": "60d"},
    "1h": {"interval": "1h", "period": "60d", "max_backfill": "60d"},
    "1d": {"interval": "1d", "period": "1y", "max_backfill": None},
    "1wk": {"interval": "1wk", "period": "5y", "max_backfill": None},
}


class YahooFinanceProvider:
    """Thin optional-yfinance provider for quotes and OHLCV records."""

    name = "yfinance"

    def __init__(self, *, timeout: int = 30) -> None:
        self.timeout = timeout

    def quote(self, symbol: str) -> dict[str, Any]:
        """Return company and quote metadata from yfinance."""
        yf = quiet_call(require_dependency, "yfinance", MARKET_INSTALL_HINT)
        symbol = symbol.strip().upper()
        if not symbol:
            raise ProviderError("symbol is required")
        ticker = quiet_call(yf.Ticker, symbol)
        info = quiet_call(lambda: ticker.info or {})
        total_cash = info.get("totalCash")
        total_debt = info.get("totalDebt")
        return {
            "symbol": symbol,
            "company_name": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "website": info.get("website"),
            "ir_website": info.get("irWebsite"),
            "last_price": info.get("regularMarketPrice") or info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "enterprise_value": info.get("enterpriseValue"),
            "shares_outstanding": info.get("sharesOutstanding") or info.get("impliedSharesOutstanding"),
            "total_revenue": info.get("totalRevenue"),
            "cash": total_cash,
            "debt": total_debt,
            "net_debt": _net_debt(total_debt, total_cash),
            "currency": info.get("currency"),
            "source": "yfinance",
        }

    def ohlcv(
        self,
        symbol: str,
        *,
        timeframe: str = "1d",
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = 200,
    ) -> list[dict[str, Any]]:
        """Fetch normalized OHLCV rows."""
        yf = quiet_call(require_dependency, "yfinance", MARKET_INSTALL_HINT)
        symbol = symbol.strip().upper()
        if timeframe not in TIMEFRAME_CONFIGS:
            raise ProviderError(f"Unsupported timeframe: {timeframe}")
        config = TIMEFRAME_CONFIGS[timeframe]
        request = {
            "interval": config["interval"],
            "auto_adjust": False,
            "timeout": self.timeout,
        }
        period, start, end = _resolve_fetch_window(timeframe, start_date=start_date, end_date=end_date)
        if period:
            request["period"] = period
        else:
            request["start"] = start
            request["end"] = end
        ticker = quiet_call(yf.Ticker, symbol)
        frame = quiet_call(ticker.history, **request)
        if frame is None or frame.empty:
            return []
        records = _normalize_history_frame(frame, symbol)
        if limit is not None:
            return records[-int(limit):]
        return records

    def financial_statement(
        self,
        symbol: str,
        *,
        statement: str = "income",
        period: str = "annual",
    ) -> dict[str, Any]:
        """Fetch a financial statement table from yfinance."""
        yf = quiet_call(require_dependency, "yfinance", MARKET_INSTALL_HINT)
        symbol = symbol.strip().upper()
        ticker = quiet_call(yf.Ticker, symbol)
        attr = _statement_attr(statement, period)
        frame = quiet_call(lambda: getattr(ticker, attr, None))
        if frame is None or frame.empty:
            return {"symbol": symbol, "statement": statement, "period": period, "rows": [], "source": "yfinance"}
        return {
            "symbol": symbol,
            "statement": statement,
            "period": period,
            "rows": _normalize_statement_frame(frame),
            "source": "yfinance",
        }

    def market_status(self, market: str = "US") -> dict[str, Any]:
        """Return Yahoo market status and major-index summary."""
        yf = quiet_call(require_dependency, "yfinance", MARKET_INSTALL_HINT)
        market_key = market.strip().upper() or "US"
        market_data = quiet_call(yf.Market, market_key, timeout=self.timeout)
        status = _to_jsonable(quiet_call(lambda: market_data.status or {}))
        summary = _normalize_market_summary(quiet_call(lambda: market_data.summary or {}))
        return {
            "market": market_key,
            "market_state": _market_state(status, summary),
            "status": status,
            "summary": summary,
            "source": "yfinance",
        }

    def company_calendar(self, symbol: str) -> dict[str, Any]:
        """Return company calendar fields such as earnings and dividend dates."""
        yf = quiet_call(require_dependency, "yfinance", MARKET_INSTALL_HINT)
        symbol = symbol.strip().upper()
        ticker = quiet_call(yf.Ticker, symbol)
        return {
            "symbol": symbol,
            "calendar": _to_jsonable(quiet_call(lambda: ticker.calendar or {})),
            "source": "yfinance",
        }

    def earnings_dates(self, symbol: str, *, limit: int = 12) -> dict[str, Any]:
        """Return historical/upcoming earnings-date rows."""
        yf = quiet_call(require_dependency, "yfinance", MARKET_INSTALL_HINT)
        symbol = symbol.strip().upper()
        ticker = quiet_call(yf.Ticker, symbol)
        row_limit = _bounded_limit(limit)
        frame = quiet_call(ticker.get_earnings_dates, limit=row_limit)
        rows = _records_from_frame(frame)[:row_limit]
        return {
            "symbol": symbol,
            "rows": rows,
            "count": len(rows),
            "source": "yfinance",
        }

    def sector_keys(self) -> dict[str, Any]:
        """Return sector keys known by the installed yfinance version."""
        return {
            "sectors": [{"key": key, "name": _title_from_key(key)} for key in _sector_industry_mapping().keys()],
            "source": "yfinance",
        }

    def sector_overview(self, key: str) -> dict[str, Any]:
        sector = self._sector(key)
        return {
            "key": sector.key,
            "name": sector.name,
            "symbol": sector.symbol,
            "overview": _to_jsonable(quiet_call(lambda: sector.overview or {})),
            "source": "yfinance",
        }

    def sector_industries(self, key: str) -> dict[str, Any]:
        sector = self._sector(key)
        rows = _records_from_frame(quiet_call(lambda: sector.industries))
        mapping = set(_sector_industry_mapping().get(sector.key, ()))
        return {
            "key": sector.key,
            "name": sector.name,
            "industries": [_with_industry_key(row, mapping) for row in rows],
            "count": len(rows),
            "source": "yfinance",
        }

    def sector_top_companies(self, key: str, *, limit: int = 25) -> dict[str, Any]:
        return self._sector_table(key, "top_companies", limit=limit)

    def sector_top_etfs(self, key: str, *, limit: int = 25) -> dict[str, Any]:
        return self._sector_table(key, "top_etfs", limit=limit)

    def sector_top_mutual_funds(self, key: str, *, limit: int = 25) -> dict[str, Any]:
        return self._sector_table(key, "top_mutual_funds", limit=limit)

    def sector_research_reports(self, key: str, *, limit: int = 25) -> dict[str, Any]:
        return self._sector_table(key, "research_reports", limit=limit)

    def industry_keys(self, *, sector: str | None = None) -> dict[str, Any]:
        mapping = _sector_industry_mapping()
        sectors = [sector.strip().lower()] if sector else list(mapping.keys())
        industries = []
        for sector_key in sectors:
            for industry_key in mapping.get(sector_key, ()):
                industries.append({
                    "key": industry_key,
                    "name": _title_from_key(industry_key),
                    "sector_key": sector_key,
                    "sector_name": _title_from_key(sector_key),
                })
        return {"industries": industries, "count": len(industries), "source": "yfinance"}

    def industry_overview(self, key: str) -> dict[str, Any]:
        industry = self._industry(key)
        return {
            "key": industry.key,
            "name": industry.name,
            "sector_key": industry.sector_key,
            "sector_name": industry.sector_name,
            "symbol": industry.symbol,
            "overview": _to_jsonable(quiet_call(lambda: industry.overview or {})),
            "source": "yfinance",
        }

    def industry_top_companies(self, key: str, *, limit: int = 25) -> dict[str, Any]:
        return self._industry_table(key, "top_companies", limit=limit)

    def industry_top_growth_companies(self, key: str, *, limit: int = 25) -> dict[str, Any]:
        return self._industry_table(key, "top_growth_companies", limit=limit)

    def industry_top_performing_companies(self, key: str, *, limit: int = 25) -> dict[str, Any]:
        return self._industry_table(key, "top_performing_companies", limit=limit)

    def industry_research_reports(self, key: str, *, limit: int = 25) -> dict[str, Any]:
        return self._industry_table(key, "research_reports", limit=limit)

    def predefined_screens(self) -> dict[str, Any]:
        yf = quiet_call(require_dependency, "yfinance", MARKET_INSTALL_HINT)
        queries = getattr(yf, "PREDEFINED_SCREENER_QUERIES", {})
        return {
            "queries": [{"key": key, "name": _title_from_key(key)} for key in sorted(queries)],
            "count": len(queries),
            "source": "yfinance",
        }

    def run_screen(
        self,
        query: str,
        *,
        count: int = 25,
        offset: int | None = None,
        sort_field: str | None = None,
        sort_asc: bool | None = None,
    ) -> dict[str, Any]:
        yf = quiet_call(require_dependency, "yfinance", MARKET_INSTALL_HINT)
        kwargs: dict[str, Any] = {"count": _bounded_limit(count)}
        if offset is not None:
            kwargs["offset"] = offset
        if sort_field:
            kwargs["sortField"] = sort_field
        if sort_asc is not None:
            kwargs["sortAsc"] = sort_asc
        payload = quiet_call(yf.screen, query, **kwargs)
        quotes = payload.get("quotes") if isinstance(payload, dict) else []
        return {
            "query": query,
            "title": payload.get("title") if isinstance(payload, dict) else None,
            "description": payload.get("description") if isinstance(payload, dict) else None,
            "quotes": [_normalize_screen_quote(row) for row in (quotes or [])],
            "count": len(quotes or []),
            "total": payload.get("total") if isinstance(payload, dict) else None,
            "source": "yfinance",
        }

    def _sector(self, key: str) -> Any:
        yf = quiet_call(require_dependency, "yfinance", MARKET_INSTALL_HINT)
        return quiet_call(yf.Sector, _normalize_sector_key(key))

    def _industry(self, key: str) -> Any:
        yf = quiet_call(require_dependency, "yfinance", MARKET_INSTALL_HINT)
        return quiet_call(yf.Industry, _normalize_industry_key(key))

    def _sector_table(self, key: str, attr: str, *, limit: int) -> dict[str, Any]:
        sector = self._sector(key)
        rows = _records_from_frame(quiet_call(lambda: getattr(sector, attr)))
        return {
            "key": sector.key,
            "name": sector.name,
            "table": attr,
            "rows": rows[: _bounded_limit(limit)],
            "count": min(len(rows), _bounded_limit(limit)),
            "source": "yfinance",
        }

    def _industry_table(self, key: str, attr: str, *, limit: int) -> dict[str, Any]:
        industry = self._industry(key)
        rows = _records_from_frame(quiet_call(lambda: getattr(industry, attr)))
        return {
            "key": industry.key,
            "name": industry.name,
            "sector_key": industry.sector_key,
            "sector_name": industry.sector_name,
            "table": attr,
            "rows": rows[: _bounded_limit(limit)],
            "count": min(len(rows), _bounded_limit(limit)),
            "source": "yfinance",
        }


def _resolve_fetch_window(
    timeframe: str,
    *,
    start_date: str | None,
    end_date: str | None,
) -> tuple[str | None, str | None, str | None]:
    config = TIMEFRAME_CONFIGS[timeframe]
    if start_date or end_date:
        return None, start_date or end_date, end_date or date.today().isoformat()
    max_backfill = config.get("max_backfill")
    if not max_backfill:
        return config["period"], None, None
    if max_backfill.endswith("d") and max_backfill[:-1].isdigit():
        days = max(1, int(max_backfill[:-1]) - 1)
        end = date.today()
        start = end - timedelta(days=days)
        return None, start.isoformat(), end.isoformat()
    return max_backfill, None, None


def _normalize_history_frame(frame: Any, symbol: str) -> list[dict[str, Any]]:
    data = frame.reset_index()
    rename_map = {
        "Date": "date",
        "Datetime": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
        "Adj Close": "adjusted_close",
    }
    data = data.rename(columns={old: new for old, new in rename_map.items() if old in data.columns})
    if "adjusted_close" not in data.columns and "close" in data.columns:
        data["adjusted_close"] = data["close"]
    rows = []
    for record in data.to_dict(orient="records"):
        row = {
            "symbol": symbol,
            "date": str(record.get("date")),
            "open": _number_or_none(record.get("open")),
            "high": _number_or_none(record.get("high")),
            "low": _number_or_none(record.get("low")),
            "close": _number_or_none(record.get("close")),
            "volume": _number_or_none(record.get("volume")),
            "adjusted_close": _number_or_none(record.get("adjusted_close")),
            "source": "yfinance",
        }
        rows.append(row)
    return rows


def _statement_attr(statement: str, period: str) -> str:
    statement_key = statement.strip().lower()
    period_key = period.strip().lower()
    quarterly = period_key in {"quarter", "quarterly", "q"}
    annual_map = {
        "income": "income_stmt",
        "income_statement": "income_stmt",
        "balance": "balance_sheet",
        "balance_sheet": "balance_sheet",
        "cashflow": "cashflow",
        "cash_flow": "cashflow",
    }
    quarterly_map = {
        "income": "quarterly_income_stmt",
        "income_statement": "quarterly_income_stmt",
        "balance": "quarterly_balance_sheet",
        "balance_sheet": "quarterly_balance_sheet",
        "cashflow": "quarterly_cashflow",
        "cash_flow": "quarterly_cashflow",
    }
    mapping = quarterly_map if quarterly else annual_map
    if statement_key not in mapping:
        raise ProviderError("statement must be one of income, balance, cashflow")
    return mapping[statement_key]


def _normalize_statement_frame(frame: Any) -> list[dict[str, Any]]:
    rows = []
    for field, values in frame.iterrows():
        row = {"field": str(field)}
        for column, value in values.items():
            row[str(column.date() if hasattr(column, "date") else column)] = _number_or_none(value)
        rows.append(row)
    return rows


def _records_from_frame(frame: Any) -> list[dict[str, Any]]:
    if frame is None:
        return []
    if hasattr(frame, "empty") and frame.empty:
        return []
    reset = frame.reset_index() if hasattr(frame, "reset_index") else frame
    records = reset.to_dict(orient="records") if hasattr(reset, "to_dict") else []
    return [_normalize_record(record) for record in records]


def _normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    return {_normalize_key(key): _to_jsonable(value) for key, value in record.items()}


def _normalize_key(key: Any) -> str:
    text = str(key).strip()
    text = re.sub(r"[^0-9A-Za-z]+", "_", text).strip("_").lower()
    return text or "value"


def _to_jsonable(value: Any) -> Any:
    if hasattr(value, "reset_index") and hasattr(value, "to_dict"):
        return _records_from_frame(value)
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if hasattr(value, "date") and hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            return _to_jsonable(value.item())
        except Exception:
            pass
    if isinstance(value, Decimal):
        numeric = float(value)
        return int(numeric) if numeric.is_integer() else numeric
    if isinstance(value, float) and value != value:
        return None
    return value


def _normalize_market_summary(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for key, row in summary.items():
        if not isinstance(row, dict):
            continue
        rows.append({
            "id": key,
            "symbol": row.get("symbol"),
            "name": row.get("shortName") or row.get("longName"),
            "price": _number_or_none(row.get("regularMarketPrice")),
            "change": _number_or_none(row.get("regularMarketChange")),
            "change_pct": _number_or_none(row.get("regularMarketChangePercent")),
            "market_state": row.get("marketState"),
            "exchange": row.get("fullExchangeName") or row.get("exchange"),
        })
    return rows


def _market_state(status: Any, summary: list[dict[str, Any]]) -> Any:
    for row in summary:
        if row.get("market_state") is not None:
            return row["market_state"]
    if isinstance(status, dict):
        return status.get("marketState") or status.get("market_state") or status.get("status")
    return None


def _sector_industry_mapping() -> dict[str, list[str]]:
    try:
        from yfinance.domain.sector import SECTOR_INDUSTY_MAPPING_LC
    except Exception as exc:
        raise ProviderError(f"yfinance sector mapping is unavailable: {exc}") from exc
    return {str(key): list(value) for key, value in SECTOR_INDUSTY_MAPPING_LC.items()}


def _normalize_sector_key(key: str) -> str:
    sector_key = key.strip().lower()
    if sector_key not in _sector_industry_mapping():
        raise ProviderError(f"unknown sector key: {key}")
    return sector_key


def _normalize_industry_key(key: str) -> str:
    industry_key = key.strip().lower()
    valid = {industry for industries in _sector_industry_mapping().values() for industry in industries}
    if industry_key not in valid:
        raise ProviderError(f"unknown industry key: {key}")
    return industry_key


def _bounded_limit(value: int) -> int:
    return min(MAX_TABLE_ROWS, max(1, int(value)))


def _title_from_key(key: str) -> str:
    return " ".join(part.capitalize() for part in key.replace("_", "-").split("-"))


def _with_industry_key(row: dict[str, Any], allowed_keys: set[str]) -> dict[str, Any]:
    name = str(row.get("name") or "")
    key = re.sub(r"[^0-9a-z]+", "-", name.lower()).strip("-")
    if key in allowed_keys:
        return {"key": key, **row}
    return row


def _normalize_screen_quote(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "symbol": row.get("symbol"),
        "name": row.get("shortName") or row.get("longName") or row.get("companyshortname"),
        "price": _number_or_none(row.get("regularMarketPrice") or row.get("intradayprice")),
        "change_pct": _number_or_none(row.get("regularMarketChangePercent") or row.get("percentchange")),
        "market_cap": _number_or_none(row.get("marketCap") or row.get("intradaymarketcap")),
        "volume": _number_or_none(row.get("regularMarketVolume") or row.get("dayvolume")),
        "sector": row.get("sector"),
        "industry": row.get("industry"),
        "exchange": row.get("exchange"),
    }


def _number_or_none(value: Any) -> float | int | None:
    if value is None:
        return None
    try:
        if isinstance(value, float) and value != value:  # NaN
            return None
        numeric = float(value)
    except (ValueError, TypeError):
        return None
    return int(numeric) if numeric.is_integer() else numeric


def _net_debt(total_debt: Any, total_cash: Any) -> float | int | None:
    debt = _number_or_none(total_debt)
    cash = _number_or_none(total_cash)
    if debt is None or cash is None:
        return None
    value = float(debt) - float(cash)
    return int(value) if value.is_integer() else value
