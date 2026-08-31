from scripts.azure.check_free_skus import (
    estimate_monthly_cost,
    evaluate,
    resolve_azure_cli,
    resource_type_supports_location,
    select_retail_price,
)


def valid_result() -> dict[str, object]:
    return {
        "authenticated": True,
        "subscription_matches": True,
        "location_available": True,
        "static_web_apps_free": True,
        "app_service_b1_linux": True,
        "container_apps_consumption": True,
        "key_vault_available": True,
        "managed_identity_available": True,
        "azure_sql_basic": True,
        "cost_management_available": True,
        "monitoring_available": True,
        "retail_prices_available": True,
        "budget_amount_usd": 30,
        "estimated_monthly_cost_usd": 17.31,
    }


def test_preflight_accepts_the_approved_paid_budget_result():
    decision = evaluate(valid_result())

    assert decision.allowed is True
    assert decision.reason == "all paid budget guards passed"


def test_windows_azure_cli_resolution_prefers_the_cmd_launcher(monkeypatch):
    candidates: list[str] = []

    def fake_which(candidate: str) -> str | None:
        candidates.append(candidate)
        return "C:/Azure/az.cmd" if candidate == "az.cmd" else None

    monkeypatch.setattr("scripts.azure.check_free_skus.shutil.which", fake_which)

    assert resolve_azure_cli("nt") == "C:/Azure/az.cmd"
    assert candidates == ["az.cmd"]


def test_posix_azure_cli_resolution_uses_the_native_executable(monkeypatch):
    monkeypatch.setattr(
        "scripts.azure.check_free_skus.shutil.which",
        lambda candidate: "/usr/bin/az" if candidate == "az" else None,
    )

    assert resolve_azure_cli("posix") == "/usr/bin/az"


def test_preflight_rejects_fixed_monthly_cost_over_twenty_dollars():
    result = valid_result() | {"estimated_monthly_cost_usd": 20.01}

    decision = evaluate(result)

    assert decision.allowed is False
    assert decision.reason == "estimated fixed monthly cost exceeds USD 20"


def test_preflight_requires_the_thirty_dollar_resource_group_budget():
    decision = evaluate(valid_result() | {"budget_amount_usd": 29.99})

    assert decision.allowed is False
    assert decision.reason == "resource group monthly budget must equal USD 30"


def test_preflight_rejects_each_missing_guard():
    expected = {
        "authenticated": "Azure CLI is not authenticated",
        "subscription_matches": "active subscription does not match the requested subscription",
        "location_available": "requested Azure location is unavailable",
        "static_web_apps_free": "Static Web Apps Free is unavailable",
        "app_service_b1_linux": "App Service Linux B1 is unavailable",
        "container_apps_consumption": "Container Apps Consumption is unavailable",
        "key_vault_available": "Azure Key Vault is unavailable",
        "managed_identity_available": "Azure Managed Identity is unavailable",
        "azure_sql_basic": "Azure SQL Basic is unavailable",
        "cost_management_available": "Microsoft.Consumption is unavailable",
        "monitoring_available": "Microsoft.Insights is unavailable",
        "retail_prices_available": "Azure Retail Prices are unavailable",
    }

    for guard, reason in expected.items():
        decision = evaluate(valid_result() | {guard: False})
        assert decision.allowed is False
        assert decision.reason == reason


def test_preflight_rejects_missing_or_invalid_cost():
    missing_cost = valid_result()
    missing_cost.pop("estimated_monthly_cost_usd")

    assert evaluate(missing_cost).allowed is False
    assert evaluate(valid_result() | {"estimated_monthly_cost_usd": "cheap"}).allowed is False


def test_static_site_provider_location_matching_accepts_display_names():
    provider = {
        "resourceTypes": [
            {"resourceType": "staticSites", "locations": ["East Asia", "West Europe"]}
        ]
    }

    assert resource_type_supports_location(provider, "staticSites", "eastasia") is True
    assert resource_type_supports_location(provider, "staticSites", "japaneast") is False


def test_monthly_cost_uses_730_app_service_hours_and_average_month_length():
    assert estimate_monthly_cost(0.017, 0.161) == 17.31


def test_retail_price_selection_uses_the_latest_exact_consumption_meter():
    items = [
        {
            "productName": "Azure App Service Basic Plan - Linux",
            "skuName": "B1",
            "meterName": "B1",
            "unitOfMeasure": "1 Hour",
            "type": "Consumption",
            "retailPrice": 0.016,
            "effectiveStartDate": "2018-01-01T00:00:00Z",
        },
        {
            "productName": "Azure App Service Basic Plan - Linux",
            "skuName": "B1",
            "meterName": "B1",
            "unitOfMeasure": "1 Hour",
            "type": "Consumption",
            "retailPrice": 0.017,
            "effectiveStartDate": "2019-06-01T00:00:00Z",
        },
        {
            "productName": "Azure App Service Basic Plan - Linux",
            "skuName": "B2",
            "meterName": "B2",
            "unitOfMeasure": "1 Hour",
            "type": "Consumption",
            "retailPrice": 0.034,
            "effectiveStartDate": "2019-06-01T00:00:00Z",
        },
    ]

    assert select_retail_price(
        items,
        product_name="Azure App Service Basic Plan - Linux",
        sku_name="B1",
        meter_name="B1",
        unit_of_measure="1 Hour",
    ) == 0.017
