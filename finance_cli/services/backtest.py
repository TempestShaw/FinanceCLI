"""Backtest request builders and VectorBT service wrappers."""
from __future__ import annotations

from typing import Any

from finance_cli.backtesting.portfolio import build_quantile_weights, build_rebalance_events, build_rebalance_snapshot
from finance_cli.backtesting.result_shaping import shape_backtest_result
from finance_cli.providers.base import ProviderError


BACKTEST_INSTALL_HINT = "Install or repair Finance CLI with: python -m pip install -U finance-cli"


def _vectorbt_engine() -> Any:
    try:
        from finance_cli.backtesting import vectorbt_engine
    except ImportError as exc:
        raise ProviderError(f"Missing backtest dependency 'vectorbt'. {BACKTEST_INSTALL_HINT}") from exc
    return vectorbt_engine


def build_strategy_backtest_payload(
    *,
    strategy_id: str,
    start_date: str,
    end_date: str,
    initial_cash: float = 100000.0,
    parameters: dict[str, Any] | None = None,
    fee_mode: str = "mixed",
    fixed_fee: float = 2.0,
    fees_pct: float = 0.001,
) -> dict[str, Any]:
    """Normalize a strategy backtest request payload."""
    return {
        "strategy_id": strategy_id,
        "start_date": start_date,
        "end_date": end_date,
        "initial_cash": float(initial_cash),
        "parameters": parameters or {},
        "fee_mode": fee_mode,
        "fixed_fee": float(fixed_fee),
        "fees_pct": float(fees_pct),
    }


def build_factor_backtest_payload(
    *,
    factor_name: str,
    symbols: list[str],
    start_date: str,
    end_date: str,
    timeframe: str = "1d",
    initial_cash: float = 100000.0,
    direction: str = "long_short",
    top_pct: float = 0.2,
    bottom_pct: float = 0.2,
    rebalance_freq: str = "monthly",
    fixed_fee: float = 2.0,
    fees_pct: float = 0.001,
) -> dict[str, Any]:
    """Normalize a factor backtest request payload."""
    return {
        "factor_name": factor_name,
        "symbols": [symbol.strip().upper() for symbol in symbols if symbol.strip()],
        "start_date": start_date,
        "end_date": end_date,
        "timeframe": timeframe,
        "initial_cash": float(initial_cash),
        "direction": direction,
        "top_pct": float(top_pct),
        "bottom_pct": float(bottom_pct),
        "rebalance_freq": rebalance_freq,
        "fixed_fee": float(fixed_fee),
        "fees_pct": float(fees_pct),
    }


def preview_factor_rebalance(
    *,
    factor_name: str,
    scores: dict[str, float],
    timestamp: str = "preview",
    direction: str = "long_short",
    top_pct: float = 0.2,
    bottom_pct: float = 0.2,
) -> dict[str, Any]:
    """Preview quantile basket construction for factor scores."""
    weights = build_quantile_weights(
        scores,
        direction=direction,
        top_pct=top_pct,
        bottom_pct=bottom_pct,
    )
    snapshot = build_rebalance_snapshot(timestamp, weights)
    events = build_rebalance_events(timestamp, weights)
    return shape_backtest_result(
        run_type="factor_rebalance_preview",
        config={
            "factor_name": factor_name,
            "timestamp": timestamp,
            "direction": direction,
            "top_pct": top_pct,
            "bottom_pct": bottom_pct,
        },
        metrics={
            "factor_name": factor_name,
            "symbols": sorted(weights),
            "weights": weights,
            "gross_exposure": snapshot["gross_exposure"],
            "net_exposure": snapshot["net_exposure"],
        },
        events=events,
        extra={"rebalance_snapshot": snapshot},
    )


def available_backtest_strategies() -> dict[str, Any]:
    """List VectorBT-backed strategy presets."""
    return {"engine": "vectorbt", "strategies": _vectorbt_engine().list_strategies()}


def describe_backtest_strategy(name: str) -> dict[str, Any]:
    """Describe one built-in or custom strategy contract."""
    payload = _vectorbt_engine().describe_strategy(name)
    payload["engine"] = "vectorbt"
    return payload


def run_backtest(
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
    service: Any | None = None,
) -> dict[str, Any]:
    """Run a VectorBT strategy backtest from normalized market data."""
    return _vectorbt_engine().run_vectorbt_backtest(
        strategy=strategy,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        timeframe=timeframe,
        initial_cash=initial_cash,
        fees=fees,
        fixed_fees=fixed_fees,
        slippage=slippage,
        provider=provider,
        params=params,
        strategy_file=strategy_file,
        plot_path=plot_path,
        service=service,
    )


def tune_backtest(
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
    """Run a bounded VectorBT parameter grid."""
    return _vectorbt_engine().tune_vectorbt_backtest(
        strategy=strategy,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        grid=grid,
        metric=metric,
        max_runs=max_runs,
        timeframe=timeframe,
        initial_cash=initial_cash,
        fees=fees,
        fixed_fees=fixed_fees,
        slippage=slippage,
        provider=provider,
        strategy_file=strategy_file,
        service=service,
    )
