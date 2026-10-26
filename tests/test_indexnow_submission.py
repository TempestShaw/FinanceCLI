import io
from unittest.mock import patch

import pytest

from scripts.notify_indexnow import BASE, KEY_LOCATION, payload_for, submit


@pytest.mark.parametrize("url", [
    "https://example.com/FinanceCLI/",
    "https://tempestshaw.github.io/OtherProject/",
    BASE + "../OtherProject/",
    BASE + "%2e%2e/OtherProject/",
    "http://tempestshaw.github.io/FinanceCLI/",
    BASE + "research-examples/?email=private",
    BASE + "research-examples/#example",
])
def test_rejects_urls_outside_canonical_docs_scope(url):
    with pytest.raises(ValueError):
        payload_for(url)


def test_payload_proves_subdirectory_ownership():
    payload = payload_for(BASE + "research-examples/")
    assert payload["host"] == "tempestshaw.github.io"
    assert payload["keyLocation"] == KEY_LOCATION
    assert payload["urlList"] == [BASE + "research-examples/"]


def test_wrong_published_key_prevents_submission():
    with patch("scripts.notify_indexnow.urlopen", return_value=io.BytesIO(b"wrong")) as send:
        with pytest.raises(ValueError, match="Published key differs"):
            submit(payload_for(BASE + "research-examples/"))
    assert send.call_count == 1


def test_accepts_pending_key_validation_response():
    payload = payload_for(BASE + "research-examples/")
    response = io.BytesIO(b"")
    response.status = 202
    with patch("scripts.notify_indexnow.urlopen", side_effect=[
        io.BytesIO(payload["key"].encode()), response,
    ]):
        assert submit(payload) == 202
