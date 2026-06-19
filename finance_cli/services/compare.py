"""Run one command across several symbols and align the results side by side.

``compare`` is a thin orchestrator: it resolves a registered sub-command, invokes
it once per symbol, and folds the per-symbol scalar metrics into a single
``metric x symbol`` matrix. The heavy lifting (fetching, parsing) stays in the
sub-command; compare only reshapes already-computed results.
"""
from __future__ import annotations

from typing import Any, Callable

from finance_cli.presentation import scalar_metrics
from finance_cli.schemas import FinanceCommandResult

CommandRunner = Callable[[str, list[str]], FinanceCommandResult]


def build_comparison(
    symbols: list[str],
    command: str,
    extra_args: list[str],
    *,
    run: CommandRunner,
) -> dict[str, Any]:
    """Invoke ``command`` for each symbol and align scalar metrics into rows."""
    metrics_by_symbol: dict[str, dict[str, str]] = {}
    ordered_labels: list[str] = []
    errors: dict[str, str] = {}
    warnings: list[str] = []

    for symbol in symbols:
        result = run(command, [symbol, *extra_args])
        if not result.ok:
            errors[symbol] = result.error or "unknown error"
            continue
        warnings.extend(result.warnings)
        pairs = scalar_metrics(result.data)
        if not pairs:
            errors[symbol] = "no comparable scalar metrics in result"
            continue
        values: dict[str, str] = {}
        for label, value in pairs:
            if label not in ordered_labels:
                ordered_labels.append(label)
            values[label] = value
        metrics_by_symbol[symbol] = values

    compared = [symbol for symbol in symbols if symbol in metrics_by_symbol]
    rows = [
        {"metric": label, **{symbol: metrics_by_symbol[symbol].get(label, "-") for symbol in compared}}
        for label in ordered_labels
    ]
    return {
        "command": command,
        "symbols": symbols,
        "compared": compared,
        "metrics": ordered_labels,
        "rows": rows,
        "errors": errors,
        "warnings": warnings,
    }
