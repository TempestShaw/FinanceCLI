"""Missing optional tools should explain how to install the capability."""
import builtins
import sys

import pytest

from finance_cli.providers.base import ProviderError
from finance_cli.providers.camelot_tables import CamelotTableProvider
from finance_cli.providers.paddle_ocr import PaddleOCRProvider
from finance_cli.services.backtest import _vectorbt_engine


@pytest.mark.parametrize("module,extra", [("camelot", "tables"), ("paddleocr", "ocr"), ("vectorbt", "backtest")])
def test_missing_optional_dependency_has_actionable_install(monkeypatch, module, extra):
    original_import = builtins.__import__

    def blocked_import(name, *args, **kwargs):
        if name == module or name.startswith(module + "."):
            raise ImportError(f"Test environment omits {module}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)
    if module == "vectorbt":
        import finance_cli.backtesting as backtesting
        monkeypatch.delitem(sys.modules, "finance_cli.backtesting.vectorbt_engine", raising=False)
        monkeypatch.delattr(backtesting, "vectorbt_engine", raising=False)
        action = _vectorbt_engine
    elif module == "paddleocr":
        action = PaddleOCRProvider()._create_pipeline
    else:
        action = lambda: CamelotTableProvider().extract_tables("missing.pdf")
    with pytest.raises(ProviderError, match=rf"finresearch-cli\[{extra}\]"):
        action()
