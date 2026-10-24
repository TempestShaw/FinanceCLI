"""Regression for edgartools 5.62 standard_concept metadata."""
from types import SimpleNamespace

from finance_cli.providers.sec_edgar.statements import _shape_standard_statement_rows


def test_standard_concept_is_not_a_financial_period():
    # Columns observed in a live Apple 2025 10-K using edgartools 5.62.1.
    record = {
        "concept": "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax",
        "label": "Net sales",
        "level": 4,
        "abstract": False,
        "standard_concept": "Revenue",
        "2025-09-27": 416161000000,
        "2024-09-28": 391035000000,
    }
    frame = SimpleNamespace(columns=list(record), to_dict=lambda **_: [record])
    statement = SimpleNamespace(render=lambda **_: SimpleNamespace(to_dataframe=lambda: frame))

    rows, periods = _shape_standard_statement_rows(
        statement, query=None, include_abstract=False, max_rows=100,
    )

    assert periods == ["2025-09-27", "2024-09-28"]
    assert "standard_concept" not in rows[0]
    assert rows[0]["2025-09-27"] == 416161000000
    assert rows[0]["2024-09-28"] == 391035000000
    assert rows[0]["concept"] == record["concept"]
