from scripts.load_test import RequestSample, evaluate_stage, summarize_samples


def test_stage_summary_calculates_error_rate_and_get_p95():
    samples = [
        RequestSample("login", "POST", 200, 0.2),
        RequestSample("habits", "GET", 200, 0.4),
        RequestSample("profile", "GET", 200, 0.8),
        RequestSample("habits", "GET", 500, 1.2),
    ]

    summary = summarize_samples(samples, health_failures=0)

    assert summary["requests"] == 4
    assert summary["errors"] == 1
    assert summary["error_rate_percent"] == 25.0
    assert summary["get_p95_seconds"] == 1.2


def test_20_and_50_user_stages_enforce_launch_thresholds():
    passing = {
        "error_rate_percent": 0.5,
        "get_p95_seconds": 2.4,
        "health_failures": 0,
    }

    assert evaluate_stage(20, passing) == []
    assert evaluate_stage(50, passing) == []
    assert evaluate_stage(50, passing | {"error_rate_percent": 1.0}) == [
        "HTTP error rate must be below 1%"
    ]
    assert evaluate_stage(50, passing | {"get_p95_seconds": 2.6}) == [
        "GET API p95 must be below 2.5 seconds"
    ]


def test_every_stage_requires_continuous_health():
    failures = evaluate_stage(
        100,
        {
            "error_rate_percent": 12.0,
            "get_p95_seconds": 8.0,
            "health_failures": 1,
        },
    )

    assert failures == ["health endpoints must remain HTTP 200"]
