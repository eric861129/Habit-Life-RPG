import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INFRA = ROOT / "infra"


def all_bicep_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in INFRA.rglob("*.bicep"))


def test_infrastructure_contains_only_approved_skus():
    text = all_bicep_text()

    assert "name: 'B1'" in text
    assert "tier: 'Basic'" in text
    assert "capacity: 1" in text
    assert "name: 'Free'" in text
    assert "tier: 'Free'" in text
    assert not re.search(r"name:\s*'(F1|S1|P[0-9]V[0-9]|GP_S_Gen5)'", text)
    assert "useFreeLimit" not in text
    assert "freeLimitExhaustionBehavior" not in text
    assert "BillOverUsage" not in text


def test_web_resources_enforce_transport_and_publish_guards():
    text = all_bicep_text()

    assert "httpsOnly: true" in text
    assert "minTlsVersion: '1.2'" in text
    assert "ftpsState: 'Disabled'" in text
    assert text.count("allow: false") >= 2


def test_app_service_uses_always_on_and_liveness_health_check():
    text = all_bicep_text()

    assert "alwaysOn: true" in text
    assert "healthCheckPath: '/health/live'" in text


def test_demo_api_adds_bounded_scale_to_zero_container_apps():
    container_app = (INFRA / "modules" / "container-app.bicep").read_text(
        encoding="utf-8"
    )
    environment = (INFRA / "modules" / "container-app-platform.bicep").read_text(
        encoding="utf-8"
    )

    assert "Microsoft.App/managedEnvironments@" in environment
    assert "appLogsConfiguration" not in environment
    assert "Microsoft.OperationalInsights/workspaces" not in all_bicep_text()
    assert "minReplicas: 0" in container_app
    assert "maxReplicas: 2" in container_app
    assert "concurrentRequests: '10'" in container_app
    assert "cpu: json('0.5')" in container_app
    assert "memory: '1Gi'" in container_app
    assert "keyVaultUrl:" in container_app
    assert "identity: runtimeIdentityId" in container_app


def test_static_web_app_remains_free_and_is_not_replaced_by_container_apps():
    static_web_app = (INFRA / "modules" / "static-web-app.bicep").read_text(
        encoding="utf-8"
    )

    assert "name: '${prefix}-web'" in static_web_app
    assert "name: 'Free'" in static_web_app
    assert "tier: 'Free'" in static_web_app
    assert "Microsoft.App" not in static_web_app


def test_database_is_capped_to_basic_five_dtu_and_two_gigabytes():
    text = all_bicep_text()

    assert "name: 'Basic'" in text
    assert "capacity: 5" in text
    assert "maxSizeBytes: 2147483648" in text
    assert "requestedBackupStorageRedundancy: 'Local'" in text
    assert "autoPauseDelay" not in text
    assert "minCapacity" not in text


def test_cost_guard_defines_budget_notifications_and_owner_action_group():
    text = all_bicep_text()
    cost_guard = (INFRA / "modules" / "cost-guard.bicep").read_text(encoding="utf-8")

    assert "Microsoft.Consumption/budgets@2024-08-01" in text
    assert "param monthlyBudgetAmountTwd int = 960" in cost_guard
    assert "amount: monthlyBudgetAmountTwd" in cost_guard
    assert "param budgetStartDate string = utcNow('yyyy-MM-01T00:00:00Z')" in cost_guard
    assert "param budgetEndDate string = '2036-08-01T00:00:00Z'" in cost_guard
    assert cost_guard.count("endDate: budgetEndDate") == 2
    assert "threshold: 50" in text
    assert "resource usd20AlertBudget" in text
    assert "name: '${prefix}-usd20-alert-budget'" in text
    assert "param usd20AlertBudgetAmountTwd int = 640" in cost_guard
    assert "amount: usd20AlertBudgetAmountTwd" in cost_guard
    assert "amount: 30" not in cost_guard
    assert "amount: 20" not in cost_guard
    assert "threshold: 80" in text
    assert text.count("threshold: 100") >= 2
    assert "thresholdType: 'Actual'" in text
    assert "thresholdType: 'Forecasted'" in text
    assert "8e3af657-a8ff-443c-a75c-2fe8c4bcb635" in text


def test_secrets_are_secure_parameters_and_never_outputs():
    text = all_bicep_text()
    output_lines = [line for line in text.splitlines() if line.strip().startswith("output ")]

    assert "@secure()\nparam sqlAdministratorPassword string" in text
    assert not any("password" in line.lower() or "secret" in line.lower() for line in output_lines)


def test_allowed_origins_are_explicitly_parameterized():
    text = all_bicep_text()

    assert "param allowedOrigins string" in text
    assert "HLR_ALLOWED_ORIGINS: allowedOrigins" in text
