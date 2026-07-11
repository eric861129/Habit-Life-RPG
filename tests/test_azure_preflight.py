from scripts.azure.check_free_skus import (
    evaluate,
    free_database_locations,
    resource_type_supports_location,
)


def valid_result() -> dict[str, object]:
    return {
        "authenticated": True,
        "subscription_matches": True,
        "location_available": True,
        "static_web_apps_free": True,
        "app_service_f1_linux": True,
        "azure_sql_free_offer": True,
        "azure_sql_free_region_compatible": True,
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
        "azure_sql_free_region_compatible": (
            "requested location conflicts with existing Azure SQL free databases"
        ),
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


def test_static_site_provider_location_matching_accepts_display_names():
    provider = {
        "resourceTypes": [
            {"resourceType": "staticSites", "locations": ["East Asia", "West Europe"]}
        ]
    }

    assert resource_type_supports_location(provider, "staticSites", "eastasia") is True
    assert resource_type_supports_location(provider, "staticSites", "japaneast") is False


def test_free_database_locations_find_only_free_offer_databases():
    databases = [
        {
            "kind": "v12.0,user,vcore,serverless,freelimit",
            "location": "West US 2",
        },
        {"kind": "v12.0,system,serverless", "location": "East Asia"},
        {"kind": "v12.0,user,vcore,serverless", "location": "Japan East"},
    ]

    assert free_database_locations(databases) == {"westus2"}


def test_preflight_rejects_location_that_conflicts_with_existing_free_database():
    existing_locations = free_database_locations(
        [
            {
                "kind": "v12.0,user,vcore,serverless,freelimit",
                "location": "westus2",
            }
        ]
    )

    east_asia = valid_result() | {
        "azure_sql_free_region_compatible": (
            not existing_locations or "eastasia" in existing_locations
        )
    }
    west_us_2 = valid_result() | {
        "azure_sql_free_region_compatible": (
            not existing_locations or "westus2" in existing_locations
        )
    }

    assert evaluate(east_asia).allowed is False
    assert evaluate(west_us_2).allowed is True
