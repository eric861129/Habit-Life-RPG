from scripts.azure.check_free_skus import evaluate


def valid_result() -> dict[str, object]:
    return {
        "authenticated": True,
        "subscription_matches": True,
        "location_available": True,
        "static_web_apps_free": True,
        "app_service_f1_linux": True,
        "azure_sql_free_offer": True,
        "estimated_monthly_cost": 0,
    }


def test_preflight_accepts_only_a_complete_zero_cost_result():
    decision = evaluate(valid_result())

    assert decision.allowed is True
    assert decision.reason == "all zero-cost guards passed"


def test_preflight_rejects_any_nonzero_cost():
    result = valid_result() | {"estimated_monthly_cost": 0.01}

    decision = evaluate(result)

    assert decision.allowed is False
    assert decision.reason == "estimated monthly cost is not zero"


def test_preflight_rejects_each_missing_guard():
    expected = {
        "authenticated": "Azure CLI is not authenticated",
        "subscription_matches": "active subscription does not match the requested subscription",
        "location_available": "requested Azure location is unavailable",
        "static_web_apps_free": "Static Web Apps Free is unavailable",
        "app_service_f1_linux": "App Service Linux F1 is unavailable",
        "azure_sql_free_offer": "Azure SQL free offer is unavailable",
    }

    for guard, reason in expected.items():
        decision = evaluate(valid_result() | {guard: False})
        assert decision.allowed is False
        assert decision.reason == reason


def test_preflight_rejects_missing_or_invalid_cost():
    missing_cost = valid_result()
    missing_cost.pop("estimated_monthly_cost")

    assert evaluate(missing_cost).allowed is False
    assert evaluate(valid_result() | {"estimated_monthly_cost": "free"}).allowed is False
