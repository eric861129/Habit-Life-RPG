from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

APP_SERVICE_PRODUCT = "Azure App Service Basic Plan - Linux"
APP_SERVICE_SKU = "B1"
APP_SERVICE_METER = "B1"
APP_SERVICE_UNIT = "1 Hour"
SQL_BASIC_PRODUCT = "SQL Database Single Basic"
SQL_BASIC_SKU = "B"
SQL_BASIC_METER = "B DTU"
SQL_BASIC_UNIT = "1/Day"
BUDGET_AMOUNT_USD = 30
MAX_FIXED_MONTHLY_COST_USD = 20
RETAIL_PRICES_ENDPOINT = "https://prices.azure.com/api/retail/prices"


@dataclass(frozen=True)
class PreflightDecision:
    allowed: bool
    reason: str


GUARDS = (
    ("authenticated", "Azure CLI is not authenticated"),
    ("subscription_matches", "active subscription does not match the requested subscription"),
    ("location_available", "requested Azure location is unavailable"),
    ("static_web_apps_free", "Static Web Apps Free is unavailable"),
    ("app_service_b1_linux", "App Service Linux B1 is unavailable"),
    ("container_apps_consumption", "Container Apps Consumption is unavailable"),
    ("key_vault_available", "Azure Key Vault is unavailable"),
    ("managed_identity_available", "Azure Managed Identity is unavailable"),
    ("azure_sql_basic", "Azure SQL Basic is unavailable"),
    ("cost_management_available", "Microsoft.Consumption is unavailable"),
    ("monitoring_available", "Microsoft.Insights is unavailable"),
    ("retail_prices_available", "Azure Retail Prices are unavailable"),
)


def evaluate(result: dict[str, object]) -> PreflightDecision:
    for key, reason in GUARDS:
        if result.get(key) is not True:
            return PreflightDecision(False, reason)

    budget = result.get("budget_amount_usd")
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget != 30:
        return PreflightDecision(False, "resource group monthly budget must equal USD 30")

    cost = result.get("estimated_monthly_cost_usd")
    if isinstance(cost, bool) or not isinstance(cost, (int, float)):
        return PreflightDecision(False, "estimated fixed monthly cost is missing or invalid")
    if cost <= 0:
        return PreflightDecision(False, "estimated fixed monthly cost must be greater than zero")
    if cost > MAX_FIXED_MONTHLY_COST_USD:
        return PreflightDecision(False, "estimated fixed monthly cost exceeds USD 20")
    return PreflightDecision(True, "all paid budget guards passed")


def resolve_azure_cli(platform_name: str = os.name) -> str:
    """解析目前平台可執行的 Azure CLI 路徑。"""
    candidates = ("az.cmd", "az") if platform_name == "nt" else ("az",)
    for candidate in candidates:
        executable = shutil.which(candidate)
        if executable:
            return executable
    raise FileNotFoundError("Azure CLI executable was not found")


def run_az(*arguments: str) -> Any:
    completed = subprocess.run(
        [resolve_azure_cli(), *arguments, "--output", "json", "--only-show-errors"],
        check=True,
        capture_output=True,
        text=True,
        timeout=90,
    )
    return json.loads(completed.stdout or "null")


def normalized_location(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def location_names(items: list[Any]) -> set[str]:
    names: set[str] = set()
    for item in items:
        if isinstance(item, str):
            names.add(normalized_location(item))
        elif isinstance(item, dict):
            for key in ("name", "displayName", "display_name"):
                value = item.get(key)
                if isinstance(value, str):
                    names.add(normalized_location(value))
    return names


def provider_registered(provider: dict[str, Any]) -> bool:
    return provider.get("registrationState") == "Registered"


def has_resource_type(provider: dict[str, Any], resource_type: str) -> bool:
    expected = resource_type.lower()
    return any(
        isinstance(item, dict) and str(item.get("resourceType", "")).lower() == expected
        for item in provider.get("resourceTypes", [])
    )


def resource_type_supports_location(
    provider: dict[str, Any],
    resource_type: str,
    location: str,
) -> bool:
    expected_type = resource_type.lower()
    expected_location = normalized_location(location)
    for item in provider.get("resourceTypes", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("resourceType", "")).lower() != expected_type:
            continue
        return expected_location in location_names(item.get("locations", []))
    return False


def sql_basic_available(editions: list[Any]) -> bool:
    for edition in editions:
        if not isinstance(edition, dict):
            continue
        values = {
            normalized_location(str(edition.get(key, "")))
            for key in ("name", "edition", "serviceLevelObjective", "service_level_objective")
        }
        if "basic" in values:
            return True
    return False


def fetch_retail_items(region: str, service_name: str) -> list[dict[str, Any]]:
    filter_value = f"armRegionName eq '{region}' and serviceName eq '{service_name}'"
    query = urlencode({"api-version": "2023-01-01-preview", "$filter": filter_value})
    next_page: str | None = f"{RETAIL_PRICES_ENDPOINT}?{query}"
    items: list[dict[str, Any]] = []

    while next_page:
        request = Request(next_page, headers={"Accept": "application/json"})
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
        page_items = payload.get("Items", [])
        if not isinstance(page_items, list):
            raise TypeError("Azure Retail Prices response has an invalid Items value")
        items.extend(item for item in page_items if isinstance(item, dict))
        raw_next_page = payload.get("NextPageLink")
        next_page = raw_next_page if isinstance(raw_next_page, str) and raw_next_page else None
    return items


def select_retail_price(
    items: list[dict[str, Any]],
    *,
    product_name: str,
    sku_name: str,
    meter_name: str,
    unit_of_measure: str,
) -> float:
    matches = [
        item
        for item in items
        if item.get("productName") == product_name
        and item.get("skuName") == sku_name
        and item.get("meterName") == meter_name
        and item.get("unitOfMeasure") == unit_of_measure
        and item.get("type") == "Consumption"
        and isinstance(item.get("retailPrice"), (int, float))
        and not isinstance(item.get("retailPrice"), bool)
        and item["retailPrice"] > 0
    ]
    if not matches:
        raise ValueError(f"Retail price not found for {product_name} / {sku_name} / {meter_name}")
    latest = max(matches, key=lambda item: str(item.get("effectiveStartDate", "")))
    return float(latest["retailPrice"])


def estimate_monthly_cost(app_service_hourly_price: float, sql_basic_daily_price: float) -> float:
    app_service_monthly = app_service_hourly_price * 730
    sql_monthly = sql_basic_daily_price * 365 / 12
    return round(app_service_monthly + sql_monthly, 2)


def collect(subscription_id: str, location: str) -> dict[str, object]:
    report: dict[str, object] = {
        "authenticated": False,
        "subscription_id": subscription_id,
        "subscription_matches": False,
        "location": location,
        "location_available": False,
        "static_web_apps_free": False,
        "app_service_b1_linux": False,
        "container_apps_consumption": False,
        "key_vault_available": False,
        "managed_identity_available": False,
        "azure_sql_basic": False,
        "cost_management_available": False,
        "monitoring_available": False,
        "retail_prices_available": False,
        "app_service_hourly_price_usd": None,
        "sql_basic_daily_price_usd": None,
        "estimated_monthly_cost_usd": None,
        "maximum_fixed_monthly_cost_usd": MAX_FIXED_MONTHLY_COST_USD,
        "budget_amount_usd": BUDGET_AMOUNT_USD,
    }

    try:
        account = run_az("account", "show", "--subscription", subscription_id)
    except (FileNotFoundError, subprocess.SubprocessError, json.JSONDecodeError):
        return report

    report["authenticated"] = isinstance(account, dict) and account.get("state") == "Enabled"
    report["subscription_matches"] = isinstance(account, dict) and account.get("id") == subscription_id
    if not report["authenticated"] or not report["subscription_matches"]:
        return report

    try:
        # Azure CLI 2.89 的 account list-locations 不接受 --subscription；
        # 前一步 account show 已驗證目前登入訂閱與指定 ID 一致。
        locations = run_az("account", "list-locations")
        web_provider = run_az(
            "provider", "show", "--namespace", "Microsoft.Web", "--subscription", subscription_id
        )
        sql_provider = run_az(
            "provider", "show", "--namespace", "Microsoft.Sql", "--subscription", subscription_id
        )
        container_apps_provider = run_az(
            "provider",
            "show",
            "--namespace",
            "Microsoft.App",
            "--subscription",
            subscription_id,
        )
        key_vault_provider = run_az(
            "provider",
            "show",
            "--namespace",
            "Microsoft.KeyVault",
            "--subscription",
            subscription_id,
        )
        managed_identity_provider = run_az(
            "provider",
            "show",
            "--namespace",
            "Microsoft.ManagedIdentity",
            "--subscription",
            subscription_id,
        )
        consumption_provider = run_az(
            "provider",
            "show",
            "--namespace",
            "Microsoft.Consumption",
            "--subscription",
            subscription_id,
        )
        insights_provider = run_az(
            "provider",
            "show",
            "--namespace",
            "Microsoft.Insights",
            "--subscription",
            subscription_id,
        )
        b1_locations = run_az(
            "appservice",
            "list-locations",
            "--linux-workers-enabled",
            "--sku",
            APP_SERVICE_SKU,
            "--subscription",
            subscription_id,
        )
        sql_editions = run_az(
            "sql", "db", "list-editions", "--location", location, "--subscription", subscription_id
        )
    except (subprocess.SubprocessError, json.JSONDecodeError):
        return report

    requested = normalized_location(location)
    report["location_available"] = isinstance(locations, list) and requested in location_names(locations)
    report["static_web_apps_free"] = (
        isinstance(web_provider, dict)
        and provider_registered(web_provider)
        and has_resource_type(web_provider, "staticSites")
        and resource_type_supports_location(web_provider, "staticSites", location)
    )
    report["app_service_b1_linux"] = (
        isinstance(b1_locations, list) and requested in location_names(b1_locations)
    )
    report["container_apps_consumption"] = (
        isinstance(container_apps_provider, dict)
        and provider_registered(container_apps_provider)
        and resource_type_supports_location(
            container_apps_provider,
            "managedEnvironments",
            location,
        )
        and resource_type_supports_location(container_apps_provider, "containerApps", location)
    )
    report["key_vault_available"] = (
        isinstance(key_vault_provider, dict)
        and provider_registered(key_vault_provider)
        and resource_type_supports_location(key_vault_provider, "vaults", location)
    )
    report["managed_identity_available"] = (
        isinstance(managed_identity_provider, dict)
        and provider_registered(managed_identity_provider)
        and resource_type_supports_location(
            managed_identity_provider,
            "userAssignedIdentities",
            location,
        )
    )
    report["azure_sql_basic"] = (
        isinstance(sql_provider, dict)
        and provider_registered(sql_provider)
        and isinstance(sql_editions, list)
        and sql_basic_available(sql_editions)
    )
    report["cost_management_available"] = (
        isinstance(consumption_provider, dict) and provider_registered(consumption_provider)
    )
    report["monitoring_available"] = (
        isinstance(insights_provider, dict) and provider_registered(insights_provider)
    )

    try:
        app_service_items = fetch_retail_items(requested, "Azure App Service")
        sql_items = fetch_retail_items(requested, "SQL Database")
        app_service_price = select_retail_price(
            app_service_items,
            product_name=APP_SERVICE_PRODUCT,
            sku_name=APP_SERVICE_SKU,
            meter_name=APP_SERVICE_METER,
            unit_of_measure=APP_SERVICE_UNIT,
        )
        sql_basic_price = select_retail_price(
            sql_items,
            product_name=SQL_BASIC_PRODUCT,
            sku_name=SQL_BASIC_SKU,
            meter_name=SQL_BASIC_METER,
            unit_of_measure=SQL_BASIC_UNIT,
        )
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return report

    report["retail_prices_available"] = True
    report["app_service_hourly_price_usd"] = app_service_price
    report["sql_basic_daily_price_usd"] = sql_basic_price
    report["estimated_monthly_cost_usd"] = estimate_monthly_cost(
        app_service_price,
        sql_basic_price,
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify HLR Azure paid budget deployment guards.")
    parser.add_argument("subscription_id")
    parser.add_argument("location")
    parser.add_argument("--output", default="artifacts/azure/preflight.json")
    args = parser.parse_args()

    report = collect(args.subscription_id, args.location)
    decision = evaluate(report)
    report["allowed"] = decision.allowed
    report["reason"] = decision.reason
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if decision.allowed else 2


if __name__ == "__main__":
    raise SystemExit(main())
