from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


REQUIRED_URLS = (
    "frontend_url",
    "backend_url",
    "health_live_url",
    "health_ready_url",
    "docs_url",
)


def validate_urls(urls: dict[str, str]) -> None:
    for key in REQUIRED_URLS:
        value = urls.get(key)
        if not value or urlparse(value).scheme != "https":
            raise ValueError(f"{key} must be an HTTPS URL")

    frontend_host = urlparse(urls["frontend_url"]).hostname or ""
    backend_host = urlparse(urls["backend_url"]).hostname or ""
    if not frontend_host.endswith(".azurestaticapps.net"):
        raise ValueError("frontend_url must use an Azure hostname")
    if not backend_host.endswith(".azurewebsites.net"):
        raise ValueError("backend_url must use an Azure hostname")
    for key in ("health_live_url", "health_ready_url", "docs_url"):
        if urlparse(urls[key]).hostname != backend_host:
            raise ValueError(f"{key} must use the backend Azure hostname")


def fetch(url: str, attempts: int = 10) -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": "HLR deployment smoke test"})
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=60) as response:
                return response.status, response.read(2_000_000).decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(min(5 * attempt, 30))
    raise RuntimeError(f"request failed after {attempts} attempts: {url}") from last_error


def verify(urls: dict[str, str]) -> dict[str, Any]:
    validate_urls(urls)
    results: dict[str, Any] = {}
    for key in REQUIRED_URLS:
        status, body = fetch(urls[key])
        if status != 200:
            raise RuntimeError(f"{key} returned HTTP {status}")
        results[key] = {"status": status}
        if key == "frontend_url" and "Habit Life RPG" not in body:
            raise RuntimeError("frontend response does not identify Habit Life RPG")
        if key == "health_live_url" and json.loads(body) != {"status": "ok"}:
            raise RuntimeError("liveness response is invalid")
        if key == "health_ready_url" and json.loads(body) != {"status": "ready"}:
            raise RuntimeError("readiness response is invalid")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the public HLR Azure deployment.")
    parser.add_argument("--urls", required=True, type=Path)
    args = parser.parse_args()
    urls = json.loads(args.urls.read_text(encoding="utf-8"))
    print(json.dumps(verify(urls), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
