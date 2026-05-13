"""VectorBT-backed strategy execution for the finance CLI."""
from __future__ import annotations

import importlib.util
import math
from collections.abc import Callable
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any

import pandas as pd
import vectorbt as vbt
from vectorbt.portfolio.enums import SizeType


@dataclass(frozen=True)
class StrategyDefinition:
    name: str
    summary: str
    parameters: dict[str, Any]
    builder: Callable[[pd.DataFrame, dict[str, Any], dict[str, Any]], pd.DataFrame]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "summary": self.summary,
            "parameters": self.parameters,
        }


def run_vectorbt_backtest(
    *,
    strategy: str,
    symbols: list[str],
    start_date: str,
    end_date: str,
    timeframe: str = "1d",
    initial_cash: float = 100000.0,
    fees: float = 0.001,
    fixed_fees: float = 0.0,
    slippage: float = 0.0,
    provider: str = "auto",
    params: dict[str, Any] | None = None,
    strategy_file: str | None = None,
    plot_path: str | None = None,
    equity_points: int = 50,
    trade_limit: int = 25,
    service: Any | None = None,
) -> dict[str, Any]:
    """Fetch OHLCV, build target weights, and execute a VectorBT portfolio."""
    normalized_symbols = _normalize_symbols(symbols)
    if not normalized_symbols:
        raise ValueError("at least one symbol is required")
    _validate_strategy_request(strategy, strategy_file)
    config = {
        "strategy": strategy,
        "symbols": normalized_symbols,
        "start_date": start_date,
        "end_date": end_date,
        "timeframe": timeframe,
        "initial_cash": float(initial_cash),
        "fees": float(fees),
        "fixed_fees": float(fixed_fees),
        "slippage": float(slippage),
        "provider": provider,
        "params": params or {},
        "strategy_file": strategy_file,
        "plot_path": plot_path,
        "engine": "vectorbt",
    }
    data = _load_close(
        normalized_symbols,
        start_date=start_date,
        end_date=end_date,
        timeframe=timeframe,
        provider=provider,
        service=service,
    )
    close = data["close"]
    weights = build_strategy_weights(strategy, close, params or {}, strategy_file=strategy_file, ohlcv=data["ohlcv"])
    portfolio = vbt.Portfolio.from_orders(
        close,
        size=weights,
        size_type=SizeType.TargetPercent,
        init_cash=float(initial_cash),
        fees=float(fees),
        fixed_fees=float(fixed_fees),
        slippage=float(slippage),
        cash_sharing=True,
        group_by=True,
        freq=_vectorbt_freq(timeframe),
    )
    return _shape_result(
        portfolio,
        config=config,
        data=data,
        weights=weights,
        plot_path=plot_path,
        equity_points=equity_points,
        trade_limit=trade_limit,
    )


def tune_vectorbt_backtest(
    *,
    strategy: str,
    symbols: list[str],
    start_date: str,
    end_date: str,
    grid: dict[str, list[Any]],
    metric: str = "sharpe_ratio",
    max_runs: int = 100,
    timeframe: str = "1d",
    initial_cash: float = 100000.0,
    fees: float = 0.001,
    fixed_fees: float = 0.0,
    slippage: float = 0.0,
    provider: str = "auto",
    strategy_file: str | None = None,
    service: Any | None = None,
) -> dict[str, Any]:
    """Run a bounded parameter grid and rank results by one metric."""
    combos = _grid_combinations(grid)
    if len(combos) > max_runs:
        raise ValueError(f"grid has {len(combos)} runs, above max_runs={max_runs}")

    _validate_strategy_request(strategy, strategy_file)
    normalized_symbols = _normalize_symbols(symbols)
    data = _load_close(
        normalized_symbols,
        start_date=start_date,
        end_date=end_date,
        timeframe=timeframe,
        provider=provider,
        service=service,
    )
    close = data["close"]
    rows = []
    for params in combos:
        weights = build_strategy_weights(strategy, close, params, strategy_file=strategy_file, ohlcv=data["ohlcv"])
        portfolio = vbt.Portfolio.from_orders(
            close,
            size=weights,
            size_type=SizeType.TargetPercent,
            init_cash=float(initial_cash),
            fees=float(fees),
            fixed_fees=float(fixed_fees),
            slippage=float(slippage),
            cash_sharing=True,
            group_by=True,
            freq=_vectorbt_freq(timeframe),
        )
        metrics = _portfolio_metrics(portfolio)
        rows.append({"params": params, "metrics": metrics, "score": metrics.get(metric)})

    ranked = sorted(rows, key=lambda row: _rank_key(row["score"]), reverse=True)
    return {
        "run_type": "vectorbt_tune",
        "engine": "vectorbt",
        "strategy": strategy,
        "symbols": normalized_symbols,
        "start_date": start_date,
        "end_date": end_date,
        "timeframe": timeframe,
        "metric": metric,
        "runs": len(rows),
        "best": ranked[0] if ranked else None,
        "results": ranked,
        "warnings": [],
    }


def list_strategies() -> list[dict[str, Any]]:
    return [definition.to_dict() for definition in STRATEGIES.values()]


def describe_strategy(name: str) -> dict[str, Any]:
    if name == "custom":
        return {
            "name": "custom",
            "summary": "Load a local Python file with generate_weights(...) or generate_signals(...).",
            "parameters": {
                "strategy_file": {"required": True, "description": "Path to a local .py file."},
                "params": {"required": False, "description": "JSON object passed to the custom function."},
            },
            "contract": CUSTOM_STRATEGY_CONTRACT,
        }
    definition = STRATEGIES.get(name)
    if not definition:
        raise ValueError(f"unknown strategy: {name}")
    return definition.to_dict()


def build_strategy_weights(
    strategy: str,
    close: pd.DataFrame,
    params: dict[str, Any],
    *,
    strategy_file: str | None = None,
    ohlcv: dict[str, pd.DataFrame] | None = None,
) -> pd.DataFrame:
    if strategy == "custom":
        if not strategy_file:
            raise ValueError("strategy_file is required for custom strategy")
        return _custom_weights(strategy_file, close, params, ohlcv or {})
    definition = STRATEGIES.get(strategy)
    if not definition:
        raise ValueError(f"unknown strategy: {strategy}")
    return _normalize_weights(definition.builder(close, params, ohlcv or {}), close)


def _buy_hold_weights(close: pd.DataFrame, params: dict[str, Any], _ohlcv: dict[str, Any]) -> pd.DataFrame:
    weights = _empty_weights(close)
    weights.iloc[0] = _equal_weights(list(close.columns))
    return weights


def _sma_cross_weights(close: pd.DataFrame, params: dict[str, Any], _ohlcv: dict[str, Any]) -> pd.DataFrame:
    fast = int(params.get("fast", 20))
    slow = int(params.get("slow", 100))
    if fast >= slow:
        raise ValueError("fast must be below slow")
    fast_ma = vbt.MA.run(close, fast)
    slow_ma = vbt.MA.run(close, slow)
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)
    return _weights_from_signals(close, entries, exits)


def _rsi_reversion_weights(close: pd.DataFrame, params: dict[str, Any], _ohlcv: dict[str, Any]) -> pd.DataFrame:
    window = int(params.get("window", 14))
    lower = float(params.get("lower", 30))
    upper = float(params.get("upper", 55))
    rsi = vbt.RSI.run(close, window).rsi
    entries = rsi < lower
    exits = rsi > upper
    return _weights_from_signals(close, entries, exits)


def _momentum_top_n_weights(close: pd.DataFrame, params: dict[str, Any], _ohlcv: dict[str, Any]) -> pd.DataFrame:
    lookback = int(params.get("lookback", 63))
    top_n = int(params.get("top_n", 3))
    rebalance = str(params.get("rebalance", "M")).upper()
    if top_n < 1:
        raise ValueError("top_n must be >= 1")
    returns = close.pct_change(lookback)
    weights = _empty_weights(close)
    for idx in _rebalance_index(close.index, rebalance):
        row = returns.loc[idx].dropna().sort_values(ascending=False)
        picks = [symbol for symbol in row.head(top_n).index if pd.notna(row[symbol])]
        if picks:
            weights.loc[idx, picks] = 1.0 / len(picks)
            weights.loc[idx, [symbol for symbol in close.columns if symbol not in picks]] = 0.0
    return weights


def _custom_weights(path: str, close: pd.DataFrame, params: dict[str, Any], ohlcv: dict[str, pd.DataFrame]) -> pd.DataFrame:
    module_path = Path(path).expanduser().resolve()
    if not module_path.exists():
        raise ValueError(f"strategy_file not found: {path}")
    spec = importlib.util.spec_from_file_location("finance_custom_strategy", module_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"could not load strategy_file: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "generate_weights"):
        raw = module.generate_weights(close=close.copy(), params=dict(params), ohlcv=ohlcv)
        return _normalize_weights(raw, close)
    if hasattr(module, "generate_signals"):
        raw = module.generate_signals(close=close.copy(), params=dict(params), ohlcv=ohlcv)
        if isinstance(raw, tuple) and len(raw) == 2:
            entries, exits = raw
        elif isinstance(raw, dict):
            entries, exits = raw.get("entries"), raw.get("exits")
        else:
            raise ValueError("generate_signals must return (entries, exits) or a dict")
        return _weights_from_signals(close, entries, exits)
    raise ValueError("custom strategy must define generate_weights(...) or generate_signals(...)")


def _load_close(
    symbols: list[str],
    *,
    start_date: str,
    end_date: str,
    timeframe: str,
    provider: str,
    service: Any | None,
) -> dict[str, Any]:
    from finance_cli.services.market_data import fetch_ohlcv_batch

    payload = fetch_ohlcv_batch(
        symbols,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        limit=None,
        provider=provider,
        service=service,
    )
    frames: dict[str, pd.DataFrame] = {}
    close_columns: dict[str, pd.Series] = {}
    sources: dict[str, str] = {}
    for symbol, entry in payload.get("symbols", {}).items():
        rows = entry.get("rows") or []
        if not rows:
            continue
        frame = pd.DataFrame(rows)
        if "date" not in frame or "close" not in frame:
            raise ValueError(f"OHLCV rows for {symbol} need date and close fields")
        frame["date"] = pd.to_datetime(frame["date"], utc=True, errors="coerce").dt.tz_convert(None)
        frame = frame.dropna(subset=["date"]).sort_values("date").drop_duplicates("date", keep="last").set_index("date")
        frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
        frame = frame.dropna(subset=["close"])
        if not frame.empty:
            frames[symbol] = frame
            close_columns[symbol] = frame["close"]
            sources[symbol] = str(entry.get("source") or "")
    if not close_columns:
        raise ValueError("no OHLCV rows available for backtest")
    close = pd.DataFrame(close_columns).dropna(how="all").ffill().dropna()
    if close.empty:
        raise ValueError("not enough aligned close data for backtest")
    return {"close": close, "ohlcv": frames, "sources": sources}


def _validate_strategy_request(strategy: str, strategy_file: str | None) -> None:
    if strategy == "custom":
        if not strategy_file:
            raise ValueError("strategy_file is required for custom strategy")
        return
    if strategy not in STRATEGIES:
        raise ValueError(f"unknown strategy: {strategy}")


def _shape_result(
    portfolio: Any,
    *,
    config: dict[str, Any],
    data: dict[str, Any],
    weights: pd.DataFrame,
    plot_path: str | None,
    equity_points: int,
    trade_limit: int,
) -> dict[str, Any]:
    value = portfolio.value()
    metrics = _portfolio_metrics(portfolio)
    result = {
        "run_type": "vectorbt_backtest",
        "engine": "vectorbt",
        "config": config,
        "metrics": metrics,
        "data": {
            "symbols": list(data["close"].columns),
            "rows": int(len(data["close"])),
            "start": _json_scalar(data["close"].index.min()),
            "end": _json_scalar(data["close"].index.max()),
            "sources": data["sources"],
        },
        "equity_curve": _series_points(value, max_points=equity_points, value_name="value"),
        "trades": _records(portfolio.trades.records_readable, limit=trade_limit),
        "orders": _records(portfolio.orders.records_readable, limit=trade_limit),
        "target_weights": _weight_events(weights, limit=trade_limit),
        "warnings": [],
    }
    if plot_path:
        path = Path(plot_path).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        portfolio.plot().write_html(str(path))
        result["plot_path"] = str(path)
    return result


def _portfolio_metrics(portfolio: Any) -> dict[str, Any]:
    stats = portfolio.stats()
    mapping = {
        "start_value": "Start Value",
        "end_value": "End Value",
        "total_return_pct": "Total Return [%]",
        "benchmark_return_pct": "Benchmark Return [%]",
        "max_drawdown_pct": "Max Drawdown [%]",
        "total_trades": "Total Trades",
        "win_rate_pct": "Win Rate [%]",
        "profit_factor": "Profit Factor",
        "expectancy": "Expectancy",
        "sharpe_ratio": "Sharpe Ratio",
        "calmar_ratio": "Calmar Ratio",
        "omega_ratio": "Omega Ratio",
        "sortino_ratio": "Sortino Ratio",
        "total_fees_paid": "Total Fees Paid",
    }
    shaped = {key: _json_scalar(stats.get(label)) for key, label in mapping.items() if label in stats}
    shaped["total_return_decimal"] = _json_scalar(portfolio.total_return())
    return shaped


def _weights_from_signals(close: pd.DataFrame, entries: Any, exits: Any) -> pd.DataFrame:
    entries_df = _bool_frame(entries, close)
    exits_df = _bool_frame(exits, close)
    weights = _empty_weights(close)
    active = {symbol: False for symbol in close.columns}
    for timestamp in close.index:
        changed = False
        for symbol in close.columns:
            if bool(exits_df.loc[timestamp, symbol]) and active[symbol]:
                active[symbol] = False
                changed = True
            if bool(entries_df.loc[timestamp, symbol]) and not active[symbol]:
                active[symbol] = True
                changed = True
        if changed:
            active_symbols = [symbol for symbol, is_active in active.items() if is_active]
            weights.loc[timestamp, :] = 0.0
            if active_symbols:
                for symbol, weight in _equal_weights(active_symbols).items():
                    weights.loc[timestamp, symbol] = weight
    return weights


def _bool_frame(value: Any, close: pd.DataFrame) -> pd.DataFrame:
    frame = pd.DataFrame(value, index=close.index, columns=close.columns)
    frame = frame.reindex(index=close.index, columns=close.columns)
    return frame.astype("boolean").fillna(False).astype(bool)


def _normalize_weights(value: Any, close: pd.DataFrame) -> pd.DataFrame:
    frame = pd.DataFrame(value, index=close.index, columns=close.columns)
    frame = frame.reindex(index=close.index, columns=close.columns)
    return frame.astype(float)


def _empty_weights(close: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(float("nan"), index=close.index, columns=close.columns)


def _equal_weights(symbols: list[str]) -> dict[str, float]:
    if not symbols:
        return {}
    weight = 1.0 / len(symbols)
    return {symbol: weight for symbol in symbols}


def _rebalance_index(index: pd.Index, freq: str) -> list[Any]:
    if freq in {"D", "DAY", "DAILY"}:
        return list(index)
    periods = pd.Series(index=index, data=index).dt.to_period("W" if freq in {"W", "WEEKLY"} else "M")
    return list(pd.Series(index=index, data=index).groupby(periods).tail(1))


def _grid_combinations(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    if not grid:
        return [{}]
    keys = list(grid)
    values = []
    for key in keys:
        raw_values = grid[key]
        if not isinstance(raw_values, list) or not raw_values:
            raise ValueError(f"grid value for {key} must be a non-empty list")
        values.append(raw_values)
    return [dict(zip(keys, combo)) for combo in product(*values)]


def _normalize_symbols(symbols: list[str]) -> list[str]:
    return [symbol.strip().upper() for symbol in symbols if symbol.strip()]


def _vectorbt_freq(timeframe: str) -> str:
    normalized = str(timeframe).lower()
    if normalized.endswith("d"):
        return f"{normalized[:-1] or '1'}D"
    if normalized.endswith("h"):
        return f"{normalized[:-1] or '1'}H"
    if normalized.endswith("m"):
        return f"{normalized[:-1] or '1'}T"
    return "1D"


def _series_points(series: Any, *, max_points: int, value_name: str) -> list[dict[str, Any]]:
    if isinstance(series, pd.DataFrame):
        series = series.iloc[:, 0]
    if max_points > 0 and len(series) > max_points:
        step = max(1, len(series) // max_points)
        series = series.iloc[::step]
    return [{"date": _json_scalar(index), value_name: _json_scalar(value)} for index, value in series.items()]


def _records(frame: pd.DataFrame, *, limit: int) -> list[dict[str, Any]]:
    if frame is None or frame.empty:
        return []
    return [
        {str(key): _json_scalar(value) for key, value in row.items()}
        for row in frame.head(limit).to_dict(orient="records")
    ]


def _weight_events(weights: pd.DataFrame, *, limit: int) -> list[dict[str, Any]]:
    changed = weights.dropna(how="all")
    return [
        {
            "date": _json_scalar(index),
            "weights": {column: _json_scalar(value) for column, value in row.dropna().items()},
        }
        for index, row in changed.head(limit).iterrows()
    ]


def _rank_key(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return float("-inf")
    if pd.isna(numeric):
        return float("-inf")
    return numeric


def _json_scalar(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    if pd.isna(value):
        return None
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return round(value, 6)
    if isinstance(value, int):
        return value
    return value


CUSTOM_STRATEGY_CONTRACT = {
    "generate_weights": "def generate_weights(close, params, ohlcv=None) -> DataFrame target weights indexed like close",
    "generate_signals": "def generate_signals(close, params, ohlcv=None) -> (entries, exits) boolean frames",
}


STRATEGIES: dict[str, StrategyDefinition] = {
    "buy_hold": StrategyDefinition(
        name="buy_hold",
        summary="Equal-weight buy and hold across all symbols.",
        parameters={},
        builder=_buy_hold_weights,
    ),
    "sma_cross": StrategyDefinition(
        name="sma_cross",
        summary="Long when a fast moving average crosses above a slow moving average.",
        parameters={
            "fast": {"default": 20, "type": "integer"},
            "slow": {"default": 100, "type": "integer"},
        },
        builder=_sma_cross_weights,
    ),
    "rsi_reversion": StrategyDefinition(
        name="rsi_reversion",
        summary="Long when RSI is below lower threshold; exit above upper threshold.",
        parameters={
            "window": {"default": 14, "type": "integer"},
            "lower": {"default": 30, "type": "number"},
            "upper": {"default": 55, "type": "number"},
        },
        builder=_rsi_reversion_weights,
    ),
    "momentum_top_n": StrategyDefinition(
        name="momentum_top_n",
        summary="Rebalance into the top N symbols by trailing return.",
        parameters={
            "lookback": {"default": 63, "type": "integer"},
            "top_n": {"default": 3, "type": "integer"},
            "rebalance": {"default": "M", "type": "string", "allowed": ["D", "W", "M"]},
        },
        builder=_momentum_top_n_weights,
    ),
}
