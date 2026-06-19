from finance_cli.cli.main import main
from finance_cli.presentation import (
    default_presentation,
    format_percent,
    humanize_label,
    humanize_number,
    present,
    render_markdown,
    scalar_metrics,
)


def test_humanize_number_uses_thousands_and_trims_decimals():
    assert humanize_number(11969.0) == "11,969"
    assert humanize_number(254453) == "254,453"
    assert humanize_number(0.04703815) == "0.047"
    assert humanize_number(3_000_000_000_000) == "3,000,000,000,000"


def test_humanize_label_uppercases_known_acronyms():
    assert humanize_label("wacc") == "WACC"
    assert humanize_label("cost_of_equity") == "cost of equity"
    assert humanize_label("pe_ratio") == "PE ratio"


def test_format_percent_two_decimals():
    assert format_percent(4.7038) == "4.70%"


def test_default_presentation_collapses_pct_pair_into_percent_headline():
    data = {
        "margin": 0.047038,
        "margin_pct": 4.7038,
        "inputs": {"numerator": 11969.0, "denominator": 254453.0},
        "method": "numerator / denominator",
    }

    presentation = present("formula.margin", data)

    assert presentation is not None
    assert presentation.headline == "margin = 4.70%"
    # inputs become their own labeled block, humanized with separators
    inputs_block = next(block for block in presentation.blocks if block.title == "Inputs")
    values = {kv.label: kv.value for kv in inputs_block.keyvalues}
    assert values == {"numerator": "11,969", "denominator": "254,453"}
    assert presentation.notes == ("method: numerator / denominator",)


def test_default_presentation_returns_none_for_list_shaped_payloads():
    payload = {"symbol": "AAPL", "filings": [{"form": "10-K"}, {"form": "10-Q"}]}

    assert default_presentation("filings.recent", payload) is None


def test_ratio_keys_render_as_percent_without_pct_twin():
    data = {"wacc": 0.0952, "weights": {"equity": 0.97, "debt": 0.03}}

    presentation = present("formula.wacc", data)

    assert presentation is not None
    assert presentation.headline == "WACC = 9.52%"


def test_scalar_metrics_skip_structural_keys():
    metrics = scalar_metrics({"symbol": "AAPL", "price": 195.0, "method": "n/a"})

    assert metrics == [("price", "195")]


def test_render_markdown_emits_headline_table_and_provenance():
    data = {"price": 195.0, "change_pct": 1.25, "source": "yahoo", "as_of": "2024-12-31"}

    markdown = render_markdown(present("market.quote", data))

    assert markdown.splitlines()[0] == "**price = 195**"
    assert "| Field | Value |" in markdown
    assert "_Source: yahoo · as of 2024-12-31_" in markdown


def test_md_output_format_for_formula_command(capsys):
    code = main(["formula.margin", "numerator=11969", "denominator=254453", "--output", "md"])
    output = capsys.readouterr().out

    assert code == 0
    assert output.startswith("**margin = 4.70%**")
    assert "| numerator | 11,969 |" in output


def test_report_output_upgrades_scalar_result_to_headline(capsys):
    code = main(["formula.margin", "numerator=11969", "denominator=254453", "--output", "report"])
    output = capsys.readouterr().out

    assert code == 0
    assert "margin = 4.70%" in output
    # no longer a raw JSON dump
    assert '"margin":' not in output
