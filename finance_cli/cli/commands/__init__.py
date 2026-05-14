"""Built-in finance CLI command registration."""
from __future__ import annotations

from finance_cli.cli.commands.backtest import register_backtest_commands
from finance_cli.cli.commands.calendar import register_calendar_commands
from finance_cli.cli.commands.document import register_document_commands
from finance_cli.cli.commands.estimates import register_estimates_commands
from finance_cli.cli.commands.filings import register_filings_commands
from finance_cli.cli.commands.formula import register_formula_commands
from finance_cli.cli.commands.ir import register_ir_commands
from finance_cli.cli.commands.fundamentals import register_fundamentals_commands
from finance_cli.cli.commands.industry import register_industry_commands
from finance_cli.cli.commands.kpi import register_kpi_commands
from finance_cli.cli.commands.market import register_market_commands
from finance_cli.cli.commands.market_data import register_market_data_commands
from finance_cli.cli.commands.news import register_news_commands
from finance_cli.cli.commands.price import register_price_commands
from finance_cli.cli.commands.research import register_research_commands
from finance_cli.cli.commands.screen import register_screen_commands
from finance_cli.cli.commands.sector import register_sector_commands
from finance_cli.cli.commands.sources import register_sources_commands
from finance_cli.cli.commands.symbol import register_symbol_commands
from finance_cli.cli.commands.transcripts import register_transcript_commands
from finance_cli.cli.commands.valuation import register_valuation_commands


def register_builtin_commands() -> None:
    register_market_commands()
    register_sources_commands()
    register_calendar_commands()
    register_market_data_commands()
    register_symbol_commands()
    register_sector_commands()
    register_industry_commands()
    register_screen_commands()
    register_news_commands()
    register_price_commands()
    register_estimates_commands()
    register_filings_commands()
    register_transcript_commands()
    register_fundamentals_commands()
    register_kpi_commands()
    register_valuation_commands()
    register_formula_commands()
    register_research_commands()
    register_backtest_commands()
    register_ir_commands()
    register_document_commands()
