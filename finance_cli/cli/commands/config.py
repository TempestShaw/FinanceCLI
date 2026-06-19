"""CLI configuration commands."""
from __future__ import annotations

from finance_cli.cli.args import KVArgs
from finance_cli.cli.config import config_path, load_config, set_config_value, unset_config_value
from finance_cli.cli.registry import FinanceCommand, register_command
from finance_cli.schemas import FinanceCommandResult


def _config_path(_args: list[str]) -> FinanceCommandResult:
    return FinanceCommandResult(ok=True, data={"path": str(config_path())})


def _config_show(_args: list[str]) -> FinanceCommandResult:
    path = config_path()
    return FinanceCommandResult(ok=True, data={"path": str(path), "exists": path.exists(), "config": load_config(path)})


def _config_set(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    key = args[0] if args and "=" not in args[0] else kv.str("key")
    value = args[1] if len(args) > 1 and "=" not in args[1] else kv.str("value")
    if key is None or value is None:
        return FinanceCommandResult(ok=False, error="config.set requires key and value")
    return FinanceCommandResult(ok=True, data=set_config_value(key, value))


def _config_unset(args: list[str]) -> FinanceCommandResult:
    kv = KVArgs(args)
    key = args[0] if args and "=" not in args[0] else kv.str("key")
    if key is None:
        return FinanceCommandResult(ok=False, error="config.unset requires key")
    return FinanceCommandResult(ok=True, data=unset_config_value(key))


def register_config_commands() -> None:
    register_command(FinanceCommand(
        "config.path",
        "Show the resolved FinanceCLI config file path",
        _config_path,
        usage="config.path",
        examples=("finance config.path",),
    ))
    register_command(FinanceCommand(
        "config.show",
        "Show the resolved FinanceCLI config",
        _config_show,
        usage="config.show",
        examples=("finance config.show",),
    ))
    register_command(FinanceCommand(
        "config.set",
        "Set a FinanceCLI config value",
        _config_set,
        usage="config.set KEY VALUE",
        examples=("finance config.set output.default table",),
    ))
    register_command(FinanceCommand(
        "config.unset",
        "Unset a FinanceCLI config value",
        _config_unset,
        usage="config.unset KEY",
        examples=("finance config.unset output.default",),
    ))
