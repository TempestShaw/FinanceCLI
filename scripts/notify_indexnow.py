"""Notify participating search engines about one newly published or changed docs URL."""
import argparse
import json
import posixpath
from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

BASE = "https://tempestshaw.github.io/FinanceCLI/"
KEY_LOCATION = BASE + "indexnow-key.txt"
KEY_FILE = Path(__file__).resolve().parents[1] / "docs-site/public/indexnow-key.txt"


def payload_for(url):
    parsed = urlsplit(url)
    path = posixpath.normpath(unquote(parsed.path)) + "/"
    if (parsed.scheme != "https" or parsed.netloc != "tempestshaw.github.io"
            or not path.startswith("/FinanceCLI/") or parsed.query or parsed.fragment):
        raise ValueError("Use a canonical HTTPS URL under /FinanceCLI/, without query or fragment.")
    return {"host": parsed.netloc, "key": KEY_FILE.read_text().strip(),
            "keyLocation": KEY_LOCATION, "urlList": [url]}


def submit(payload):
    with urlopen(KEY_LOCATION, timeout=20) as response:
        if response.read().decode().strip() != payload["key"]:
            raise ValueError("Published key differs: deploy the key file before notifying IndexNow.")
    request = Request("https://api.indexnow.org/indexnow",
                      data=json.dumps(payload).encode(),
                      headers={"Content-Type": "application/json; charset=utf-8",
                               "User-Agent": "FinanceCLI-IndexNow/1.0"})
    with urlopen(request, timeout=30) as response:
        if response.status not in (200, 202):
            raise ValueError(f"Unexpected IndexNow response: {response.status}")
        return response.status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="A URL added, updated or deleted since IndexNow was enabled.")
    parser.add_argument("--submit", action="store_true", help="Send the notification; default is a dry run.")
    args = parser.parse_args()
    payload = payload_for(args.url)
    status = submit(payload) if args.submit else None
    print(json.dumps({"url": args.url, "key_location": KEY_LOCATION,
                      "submitted": args.submit, "http_status": status,
                      "key_validation_pending": status == 202, "indexed": None}, indent=2))
