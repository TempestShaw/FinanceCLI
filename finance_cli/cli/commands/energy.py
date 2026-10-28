"""EIA energy inventory and electricity commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.providers.base import ProviderError
from finance_cli.providers.eia import EIAProvider
from finance_cli.schemas import FinanceCommandResult


def _energy_inventory(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    try:
        data = EIAProvider().inventory(product=kv.str("product", "crude") or "crude",
                                       country=kv.str("country", "US") or "US", limit=kv.int("limit", 20))
        return FinanceCommandResult(ok=True, data=data, warnings=data["warnings"])
    except (ProviderError, ValueError) as exc:
        return FinanceCommandResult(ok=False, error=str(exc))


def _energy_electricity(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    try:
        data = EIAProvider().electricity(region=kv.str("region", "TX") or "TX",
                                         frequency=kv.str("frequency", "monthly") or "monthly",
                                         limit=kv.int("limit", 20))
        return FinanceCommandResult(ok=True, data=data, warnings=data["warnings"])
    except (ProviderError, ValueError) as exc:
        return FinanceCommandResult(ok=False, error=str(exc))


def register_energy_commands() -> None:
    register_command(FinanceCommand(
        "energy.inventory", "Read weekly EIA US petroleum or natural-gas inventories", _energy_inventory,
        usage="energy.inventory [product=crude|gasoline|distillate|natural_gas country=US limit=20]",
        examples=("finance energy.inventory product=crude limit=12",
                  "finance energy.inventory product=natural_gas limit=12"),
        notes=("Requires EIA_API_KEY. Crude excludes SPR; natural_gas covers the Lower 48 states.",
               "Values retain the source units; petroleum is thousand barrels and natural gas is billion cubic feet.",),
    ))
    register_command(FinanceCommand(
        "energy.electricity", "Read EIA electricity retail sales and average price by state", _energy_electricity,
        usage="energy.electricity [region=TX frequency=monthly|annual limit=20]",
        examples=("finance energy.electricity region=TX frequency=monthly limit=12",),
        notes=("Requires EIA_API_KEY. region is a US state code or US; returns all-sector retail sales and prices.",
               "Retains sales/price source units. Periods describe consumption months or years, not publication dates.",),
    ))
