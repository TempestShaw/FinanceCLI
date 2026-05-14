"""Yahoo Finance provider."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from finance_cli.providers.base import ProviderError, quiet_call, require_dependency


MARKET_INSTALL_HINT = "Install or repair Finance CLI with: python -m pip install -U finresearch-cli"


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
