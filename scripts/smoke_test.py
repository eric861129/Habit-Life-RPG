from __future__ import annotations

import argparse
import json
import time
from uuid import uuid4
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
        except HTTPError as error:
            if error.code < 500 and error.code not in {408, 429}:
                raise RuntimeError(f"request returned HTTP {error.code}: {url}") from error
            last_error = error
            if attempt < attempts:
                time.sleep(min(5 * attempt, 30))
        except (URLError, TimeoutError) as error:
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


def api_request(
    method: str,
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
) -> tuple[int, Any]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "HLR deployment reader-journey test",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=120) as response:
            body = response.read(2_000_000)
            return response.status, parse_response_body(body)
    except HTTPError as error:
        body = error.read(2_000_000)
        return error.code, parse_response_body(body)


def parse_response_body(body: bytes) -> Any:
    if not body:
        return None
    decoded = body.decode("utf-8", errors="replace")
    try:
        return json.loads(decoded)
    except json.JSONDecodeError:
        return decoded


def verify_reader_journey(urls: dict[str, str], *, request=api_request) -> dict[str, int]:
    validate_urls(urls)
    api = urls["backend_url"].rstrip("/")
    suffix = uuid4().hex[:12]
    credentials = {
        "username": f"smoke-{suffix}",
        "password": f"Smoke-{uuid4().hex}!",
    }
    result: dict[str, int] = {}

    status, register = request(
        "POST", f"{api}/api/v1/auth/register", payload=credentials
    )
    if status != 201 or not isinstance(register, dict) or not register.get("access_token"):
        raise RuntimeError(f"reader registration failed with HTTP {status}")
    result["register"] = status

    status, login = request("POST", f"{api}/api/v1/auth/login", payload=credentials)
    if status != 200 or not isinstance(login, dict) or not login.get("access_token"):
        raise RuntimeError(f"reader login failed with HTTP {status}")
    token = str(login["access_token"])
    result["login"] = status

    status, habit = request(
        "POST",
        f"{api}/api/v1/habits",
        payload={"title": "部署驗收", "category": "品質"},
        token=token,
    )
    if status != 201 or not isinstance(habit, dict) or not isinstance(habit.get("id"), int):
        raise RuntimeError(f"habit creation failed with HTTP {status}")
    habit_id = habit["id"]
    result["create_habit"] = status

    status, habits = request("GET", f"{api}/api/v1/habits", token=token)
    if (
        status != 200
        or not isinstance(habits, list)
        or not any(item.get("id") == habit_id for item in habits if isinstance(item, dict))
    ):
        raise RuntimeError(f"active habit listing failed with HTTP {status}")
    result["list_habits"] = status

    checkin_url = f"{api}/api/v1/habits/{habit_id}/checkins"
    status, checkin = request("POST", checkin_url, token=token)
    if (
        status != 201
        or not isinstance(checkin, dict)
        or checkin.get("streak_count") != 1
        or int(checkin.get("exp_earned", 0)) <= 0
        or int(checkin.get("gold_earned", 0)) <= 0
    ):
        raise RuntimeError(f"habit check-in or rewards failed with HTTP {status}")
    result["checkin"] = status

    status, _ = request("POST", checkin_url, token=token)
    if status != 409:
        raise RuntimeError(f"duplicate check-in returned HTTP {status}, expected 409")
    result["duplicate_checkin"] = status

    status, profile = request("GET", f"{api}/api/v1/user/profile", token=token)
    if (
        status != 200
        or not isinstance(profile, dict)
        or int(profile.get("exp", 0)) <= 0
        or int(profile.get("gold", 0)) <= 0
    ):
        raise RuntimeError(f"rewarded profile verification failed with HTTP {status}")
    result["profile"] = status

    status, _ = request("DELETE", f"{api}/api/v1/habits/{habit_id}", token=token)
    if status != 204:
        raise RuntimeError(f"habit archive failed with HTTP {status}")
    result["archive"] = status
    return result


def run_checks(urls: dict[str, str], *, read_only: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"urls": verify(urls)}
    if not read_only:
        result["reader_journey"] = verify_reader_journey(urls)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the public HLR Azure deployment.")
    parser.add_argument("--urls", required=True, type=Path)
    parser.add_argument(
        "--read-only",
        action="store_true",
        help="check public URLs without creating a reader account or application data",
    )
    args = parser.parse_args()
    urls = json.loads(args.urls.read_text(encoding="utf-8"))
    result = run_checks(urls, read_only=args.read_only)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
