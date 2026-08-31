from __future__ import annotations

import argparse
import json
import math
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

try:
    from scripts.smoke_test import validate_urls
except ModuleNotFoundError:  # pragma: no cover - 支援直接執行 scripts/load_test.py
    from smoke_test import validate_urls


@dataclass(frozen=True)
class LoadStage:
    concurrency: int
    duration_seconds: int


@dataclass(frozen=True)
class RequestSample:
    endpoint: str
    method: str
    status: int
    elapsed_seconds: float


DEFAULT_STAGES = (
    LoadStage(20, 10 * 60),
    LoadStage(50, 5 * 60),
    LoadStage(100, 60),
)


def percentile(values: list[float], percent: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(percent * len(ordered)) - 1)
    return round(ordered[index], 3)


def summarize_samples(samples: list[RequestSample], *, health_failures: int) -> dict[str, Any]:
    errors = sum(sample.status < 200 or sample.status >= 400 for sample in samples)
    get_latencies = [
        sample.elapsed_seconds
        for sample in samples
        if sample.method == "GET" and sample.endpoint in {"habits", "profile"}
    ]
    status_counts = Counter(str(sample.status) for sample in samples)
    return {
        "requests": len(samples),
        "errors": errors,
        "error_rate_percent": round(errors * 100 / len(samples), 3) if samples else 100.0,
        "get_p95_seconds": percentile(get_latencies, 0.95),
        "health_failures": health_failures,
        "status_counts": dict(sorted(status_counts.items())),
    }


def evaluate_stage(concurrency: int, summary: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if concurrency in {20, 50}:
        if float(summary["error_rate_percent"]) >= 1:
            failures.append("HTTP error rate must be below 1%")
        p95 = summary.get("get_p95_seconds")
        if not isinstance(p95, (int, float)) or p95 >= 2.5:
            failures.append("GET API p95 must be below 2.5 seconds")
    if int(summary["health_failures"]) > 0:
        failures.append("health endpoints must remain HTTP 200")
    return failures


def request_json(
    method: str,
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
    timeout: int = 30,
) -> tuple[int, Any, float]:
    headers = {"Accept": "application/json", "User-Agent": "HLR book launch load test"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, data=data, headers=headers, method=method)
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(2_000_000)
            return response.status, parse_body(body), time.perf_counter() - started
    except HTTPError as error:
        return error.code, parse_body(error.read(2_000_000)), time.perf_counter() - started
    except (URLError, TimeoutError, OSError):
        return 0, None, time.perf_counter() - started


def parse_body(body: bytes) -> Any:
    if not body:
        return None
    try:
        return json.loads(body.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None


def create_load_account(api: str) -> dict[str, str]:
    credentials = {
        "username": f"load-{uuid4().hex[:12]}",
        "password": f"Load-{uuid4().hex}!",
    }
    status, body, _ = request_json(
        "POST", f"{api}/api/v1/auth/register", payload=credentials, timeout=120
    )
    if status != 201 or not isinstance(body, dict) or not body.get("access_token"):
        raise RuntimeError(f"load-test account registration failed with HTTP {status}")
    return credentials


def virtual_user(
    api: str,
    credentials: dict[str, str],
    duration_seconds: int,
    think_time_seconds: float,
    start_event: threading.Event,
    samples: list[RequestSample],
) -> None:
    start_event.wait()
    deadline = time.monotonic() + duration_seconds
    status, body, elapsed = request_json(
        "POST", f"{api}/api/v1/auth/login", payload=credentials
    )
    samples.append(RequestSample("login", "POST", status, elapsed))
    token = body.get("access_token") if status == 200 and isinstance(body, dict) else None
    if not token:
        return

    while time.monotonic() < deadline:
        for endpoint, path in (
            ("habits", "/api/v1/habits"),
            ("profile", "/api/v1/user/profile"),
        ):
            read_status, _, read_elapsed = request_json(
                "GET", f"{api}{path}", token=str(token)
            )
            samples.append(RequestSample(endpoint, "GET", read_status, read_elapsed))
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(think_time_seconds, remaining))


def monitor_health(
    urls: dict[str, str],
    stop_event: threading.Event,
    failures: list[str],
) -> None:
    while not stop_event.is_set():
        for key in ("health_live_url", "health_ready_url"):
            status, _, _ = request_json("GET", urls[key])
            if status != 200:
                failures.append(f"{key}:{status}")
        stop_event.wait(5)


def run_stage(
    urls: dict[str, str],
    credentials: dict[str, str],
    stage: LoadStage,
    *,
    think_time_seconds: float,
) -> dict[str, Any]:
    api = urls["backend_url"].rstrip("/")
    samples: list[RequestSample] = []
    health_failures: list[str] = []
    start_event = threading.Event()
    stop_event = threading.Event()
    health_thread = threading.Thread(
        target=monitor_health,
        args=(urls, stop_event, health_failures),
        daemon=True,
    )
    health_thread.start()
    with ThreadPoolExecutor(max_workers=stage.concurrency) as executor:
        futures = [
            executor.submit(
                virtual_user,
                api,
                credentials,
                stage.duration_seconds,
                think_time_seconds,
                start_event,
                samples,
            )
            for _ in range(stage.concurrency)
        ]
        start_event.set()
        for future in futures:
            future.result()
    stop_event.set()
    health_thread.join(timeout=10)
    summary = summarize_samples(samples, health_failures=len(health_failures))
    summary["concurrency"] = stage.concurrency
    summary["duration_seconds"] = stage.duration_seconds
    summary["failures"] = evaluate_stage(stage.concurrency, summary)
    summary["passed"] = not summary["failures"]
    return summary


def verify_recovery(urls: dict[str, str], *, timeout_seconds: int = 120) -> dict[str, Any]:
    started = time.monotonic()
    consecutive_successes = 0
    attempts = 0
    while time.monotonic() - started <= timeout_seconds:
        attempts += 1
        statuses = [
            request_json("GET", urls[key])[0]
            for key in ("backend_url", "health_live_url", "health_ready_url")
        ]
        if statuses == [200, 200, 200]:
            consecutive_successes += 1
            if consecutive_successes >= 2:
                return {
                    "passed": True,
                    "recovered_seconds": round(time.monotonic() - started, 1),
                    "attempts": attempts,
                }
        else:
            consecutive_successes = 0
        time.sleep(10)
    return {"passed": False, "recovered_seconds": None, "attempts": attempts}


def parse_stage(value: str) -> LoadStage:
    try:
        concurrency, duration = (int(part) for part in value.split(":", maxsplit=1))
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError("stage must use CONCURRENCY:DURATION_SECONDS") from error
    if concurrency <= 0 or duration <= 0:
        raise argparse.ArgumentTypeError("stage values must be positive")
    return LoadStage(concurrency, duration)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the HLR book-launch read-mostly load gate.")
    parser.add_argument("--urls", required=True, type=Path)
    parser.add_argument("--stage", action="append", type=parse_stage)
    parser.add_argument("--think-time", type=float, default=1.0)
    args = parser.parse_args()
    if args.think_time < 0:
        parser.error("--think-time must not be negative")

    urls = json.loads(args.urls.read_text(encoding="utf-8"))
    validate_urls(urls)
    api = urls["backend_url"].rstrip("/")
    credentials = create_load_account(api)
    stages = tuple(args.stage) if args.stage else DEFAULT_STAGES
    report: dict[str, Any] = {"account_created": True, "stages": []}
    for stage in stages:
        print(
            f"Starting {stage.concurrency} users for {stage.duration_seconds} seconds...",
            flush=True,
        )
        result = run_stage(
            urls,
            credentials,
            stage,
            think_time_seconds=args.think_time,
        )
        report["stages"].append(result)
        print(json.dumps(result, sort_keys=True), flush=True)

    print("Checking two-minute recovery window...", flush=True)
    report["recovery"] = verify_recovery(urls)
    report["passed"] = all(stage["passed"] for stage in report["stages"]) and report[
        "recovery"
    ]["passed"]
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
