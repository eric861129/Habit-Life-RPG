from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PreflightDecision:
    allowed: bool
    reason: str


GUARDS = (
    ("authenticated", "Azure CLI is not authenticated"),
    ("subscription_matches", "active subscription does not match the requested subscription"),
    ("location_available", "requested Azure location is unavailable"),
    ("static_web_apps_free", "Static Web Apps Free is unavailable"),
    ("app_service_f1_linux", "App Service Linux F1 is unavailable"),
    ("azure_sql_free_offer", "Azure SQL free offer is unavailable"),
    (
        "azure_sql_free_region_compatible",
        "requested location conflicts with existing Azure SQL free databases",
    ),
)


def evaluate(result: dict[str, object]) -> PreflightDecision:
    for key, reason in GUARDS:
        if result.get(key) is not True:
            return PreflightDecision(False, reason)

    cost = result.get("estimated_monthly_cost")
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost != 0:
        return PreflightDecision(False, "estimated monthly cost is not zero")
    return PreflightDecision(True, "all zero-cost guards passed")


def run_az(*arguments: str) -> Any:
    completed = subprocess.run(
        ["az", *arguments, "--output", "json", "--only-show-errors"],
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


def free_database_locations(databases: list[Any]) -> set[str]:
    return {
        normalized_location(str(database.get("location", "")))
        for database in databases
        if isinstance(database, dict)
        and "freelimit" in str(database.get("kind", "")).lower()
        and database.get("location")
    }


def collect(subscription_id: str, location: str) -> dict[str, object]:
    report: dict[str, object] = {
        "authenticated": False,
        "subscription_id": subscription_id,
        "subscription_matches": False,
        "location": location,
        "location_available": False,
        "static_web_apps_free": False,
        "app_service_f1_linux": False,
        "azure_sql_free_offer": False,
        "azure_sql_free_region_compatible": False,
        "existing_free_database_locations": [],
        "estimated_monthly_cost": None,
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
        locations = run_az("account", "list-locations")
        web_provider = run_az(
            "provider", "show", "--namespace", "Microsoft.Web", "--subscription", subscription_id
        )
        sql_provider = run_az(
            "provider", "show", "--namespace", "Microsoft.Sql", "--subscription", subscription_id
        )
        f1_locations = run_az(
            "appservice",
            "list-locations",
            "--linux-workers-enabled",
            "--sku",
            "F1",
            "--subscription",
            subscription_id,
        )
        sql_editions = run_az(
            "sql", "db", "list-editions", "--location", location, "--subscription", subscription_id
        )
        databases = run_az(
            "resource",
            "list",
            "--resource-type",
            "Microsoft.Sql/servers/databases",
            "--subscription",
            subscription_id,
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
    report["app_service_f1_linux"] = (
        isinstance(f1_locations, list) and requested in location_names(f1_locations)
    )
    sql_general_purpose = isinstance(sql_editions, list) and any(
        isinstance(item, dict)
        and "generalpurpose" in normalized_location(str(item.get("name", "")))
        for item in sql_editions
    )
    report["azure_sql_free_offer"] = (
        isinstance(sql_provider, dict)
        and provider_registered(sql_provider)
        and sql_general_purpose
    )
    existing_free_locations = (
        free_database_locations(databases) if isinstance(databases, list) else set()
    )
    report["existing_free_database_locations"] = sorted(existing_free_locations)
    report["azure_sql_free_region_compatible"] = (
        not existing_free_locations or requested in existing_free_locations
    )

    if all(report.get(key) is True for key, _ in GUARDS):
        report["estimated_monthly_cost"] = 0
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify HLR Azure zero-cost deployment guards.")
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
