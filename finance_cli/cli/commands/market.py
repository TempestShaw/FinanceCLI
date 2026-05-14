"""Market finance CLI commands."""
from __future__ import annotations

from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.core.market import get_market_regime, get_sector_heat
from finance_cli.schemas import FinanceCommandResult
from finance_cli.services.market_data import fetch_market_status


def _market_regime(args: list[str]) -> FinanceCommandResult:
    market = args[0] if len(args) >= 1 else "US"
    timeframe = args[1] if len(args) >= 2 else "swing"
    return FinanceCommandResult(ok=True, data=get_market_regime(market, timeframe).to_dict())


def _sector_heat(args: list[str]) -> FinanceCommandResult:
    market = args[0] if len(args) >= 1 else "US"
    lookback_days = int(args[1]) if len(args) >= 2 else 20
    group_by = args[2] if len(args) >= 3 else "sector"
    return FinanceCommandResult(ok=True, data=get_sector_heat(market, lookback_days, group_by).to_dict())


def _market_status(args: list[str]) -> FinanceCommandResult:
    market = args[0] if args else "US"
    return FinanceCommandResult(ok=True, data=fetch_market_status(market))


def register_market_commands() -> None:
    register_command(FinanceCommand(
        "market.regime",
        "Show market regime context",
        _market_regime,
        usage="market.regime [MARKET=US] [TIMEFRAME=swing]",
        examples=("finance market.regime US swing",),
    ))
    register_command(FinanceCommand(
        "market.sector_heat",
        "Show sector heat rankings",
        _sector_heat,
        usage="market.sector_heat [MARKET=US] [LOOKBACK_DAYS=20] [GROUP_BY=sector]",
        examples=("finance market.sector_heat US 20 sector",),
    ))
    register_command(FinanceCommand(
        "market.status",
        "Show Yahoo market open/close status and index summary",
        _market_status,
        usage="market.status [MARKET=US]",
        examples=("finance market.status US",),
    ))
