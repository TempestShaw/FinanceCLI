import pytest


@pytest.fixture(autouse=True)
def isolate_finance_cli_config(monkeypatch, tmp_path):
    monkeypatch.delenv("FINANCECLI_OUTPUT", raising=False)
    monkeypatch.setenv("FINANCECLI_CONFIG", str(tmp_path / "finance-cli-config.toml"))
