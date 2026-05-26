from finance_cli.cli.usage import parse_usage_params


def test_parse_usage_params_extracts_keys_required_flags_and_enums():
    params = parse_usage_params(
        "document.scan SOURCE|source=PATH_OR_URL "
        "[query=TEXT format=pdf|html match=fuzzy|all_terms max_chars=12000]"
    )

    assert params["source"]["required"] is True
    assert params["source"]["aliases"] == ["SOURCE"]
    assert params["format"]["enum"] == ["pdf", "html"]
    assert params["match"]["enum"] == ["fuzzy", "all_terms"]
    assert params["max_chars"]["default"] == 12000
