from io import BytesIO
from pathlib import Path
import re
from urllib.error import HTTPError

import pytest

from scripts.smoke_test import api_request, fetch, run_checks, validate_urls, verify_reader_journey


ROOT = Path(__file__).resolve().parents[1]


def valid_urls() -> dict[str, str]:
    return {
        "frontend_url": "https://hlr.example.azurestaticapps.net",
        "backend_url": "https://hlr-api.azurewebsites.net",
        "health_live_url": "https://hlr-api.azurewebsites.net/health/live",
        "health_ready_url": "https://hlr-api.azurewebsites.net/health/ready",
        "docs_url": "https://hlr-api.azurewebsites.net/docs",
    }


def test_smoke_urls_require_https_and_expected_azure_hosts():
    validate_urls(valid_urls())

    with pytest.raises(ValueError, match="HTTPS"):
        validate_urls(valid_urls() | {"frontend_url": "http://example.com"})
    with pytest.raises(ValueError, match="Azure hostname"):
        validate_urls(valid_urls() | {"backend_url": "https://example.com"})


def test_reader_journey_verifies_auth_habits_rewards_and_duplicate_checkin():
    calls: list[tuple[str, str]] = []
    checkin_responses = [
        (
            201,
            {
                "streak_count": 1,
                "exp_earned": 20,
                "gold_earned": 5,
            },
        ),
        (409, {"detail": "Habit already checked in today."}),
    ]

    def fake_request(method, url, *, payload=None, token=None):
        calls.append((method, url))
        responses = {
            ("POST", "/api/v1/auth/register"): (201, {"access_token": "register-token"}),
            ("POST", "/api/v1/auth/login"): (200, {"access_token": "login-token"}),
            ("POST", "/api/v1/habits"): (201, {"id": 42, "title": "部署驗收"}),
            ("GET", "/api/v1/habits"): (
                200,
                [{"id": 42, "title": "部署驗收", "is_archived": False}],
            ),
            ("POST", "/api/v1/habits/42/checkins"): checkin_responses,
            ("GET", "/api/v1/user/profile"): (
                200,
                {"exp": 20, "gold": 5, "level": 1},
            ),
            ("DELETE", "/api/v1/habits/42"): (204, None),
        }
        path = url.removeprefix("https://hlr-api.azurewebsites.net")
        response = responses[(method, path)]
        if isinstance(response, list):
            return response.pop(0)
        return response

    result = verify_reader_journey(valid_urls(), request=fake_request)

    assert result == {
        "archive": 204,
        "checkin": 201,
        "create_habit": 201,
        "duplicate_checkin": 409,
        "login": 200,
        "list_habits": 200,
        "profile": 200,
        "register": 201,
    }
    assert len(calls) == 8


def test_api_request_preserves_non_json_error_body(monkeypatch):
    def fail_with_plain_text(*args, **kwargs):
        raise HTTPError(
            "https://hlr-api.azurewebsites.net/api/v1/auth/register",
            500,
            "Internal Server Error",
            {},
            BytesIO(b"Internal Server Error"),
        )

    monkeypatch.setattr("scripts.smoke_test.urlopen", fail_with_plain_text)

    assert api_request(
        "POST",
        "https://hlr-api.azurewebsites.net/api/v1/auth/register",
        payload={"username": "reader", "password": "long-enough-password"},
    ) == (500, "Internal Server Error")


def test_fetch_does_not_retry_a_permanent_404(monkeypatch):
    attempts = 0

    def fail_with_not_found(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        raise HTTPError(
            "https://hlr-api.azurewebsites.net/missing",
            404,
            "Not Found",
            {},
            BytesIO(b"Not Found"),
        )

    monkeypatch.setattr("scripts.smoke_test.urlopen", fail_with_not_found)
    monkeypatch.setattr("scripts.smoke_test.time.sleep", lambda seconds: None)

    with pytest.raises(RuntimeError, match="HTTP 404"):
        fetch("https://hlr-api.azurewebsites.net/missing")

    assert attempts == 1


def test_read_only_smoke_never_runs_the_mutating_reader_journey(monkeypatch):
    monkeypatch.setattr("scripts.smoke_test.verify", lambda urls: {"frontend_url": {"status": 200}})

    def unexpected_journey(urls):
        raise AssertionError("read-only monitoring must not create reader data")

    monkeypatch.setattr("scripts.smoke_test.verify_reader_journey", unexpected_journey)

    assert run_checks(valid_urls(), read_only=True) == {
        "urls": {"frontend_url": {"status": 200}}
    }


def test_deploy_script_requires_guards_before_resource_creation():
    text = (ROOT / "scripts" / "azure" / "deploy.sh").read_text(encoding="utf-8")

    preflight = text.index("preflight.sh")
    what_if = text.index("deployment sub what-if")
    create = text.index("deployment sub create")
    assert preflight < what_if < create
    assert "HLR_DEPLOY_CONFIRMED" in text
    assert "*.local.json" in text
    assert "BillOverUsage" not in text
    assert "approved paid budget settings" in text


def test_deploy_script_scopes_subscription_deployment_name_to_location():
    text = (ROOT / "scripts" / "azure" / "deploy.sh").read_text(encoding="utf-8")

    assert 'DEPLOYMENT_NAME="hlr-book-v2-${LOCATION}"' in text


def test_deploy_script_requires_an_immutable_container_image_for_side_by_side_api():
    text = (ROOT / "scripts" / "azure" / "deploy.sh").read_text(encoding="utf-8")

    assert "HLR_DEPLOY_CONTAINER_APP" in text
    assert "HLR_CONTAINER_IMAGE" in text
    assert "deployContainerApp=true" in text
    assert "containerImage=$HLR_CONTAINER_IMAGE" in text
    assert "containerBackendHostname" in text
    assert "does not change the Static Web Apps resource or hostname" in text


def test_deployment_workflows_test_before_deploying():
    backend = (ROOT / ".github" / "workflows" / "deploy-backend.yml").read_text(
        encoding="utf-8"
    )
    frontend = (ROOT / ".github" / "workflows" / "deploy-frontend.yml").read_text(
        encoding="utf-8"
    )

    for workflow in (backend, frontend):
        assert "needs: test" in workflow
        assert "environment: azure-demo" in workflow
    assert "id-token: write" in backend
    assert "npm test -- --run" in frontend
    assert "python -m pytest -q" in backend


def test_backend_container_runs_as_non_root_without_baking_secrets():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")

    assert "USER 10001" in dockerfile
    assert "EXPOSE 8000" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "backend.app.main:app" in dockerfile
    assert "org.opencontainers.image.source" in dockerfile
    assert "DATABASE_PASSWORD" not in dockerfile
    assert "HLR_JWT_SECRET" not in dockerfile
    assert "COPY . ." not in dockerfile
    assert ".env" in dockerignore
    assert ".git" in dockerignore


def test_backend_workflow_builds_scans_and_deploys_an_immutable_image():
    backend = (ROOT / ".github" / "workflows" / "deploy-backend.yml").read_text(
        encoding="utf-8"
    )

    assert "packages: write" in backend
    assert re.search(r"docker/build-push-action@[0-9a-f]{40} # v6", backend)
    assert re.search(r"docker/metadata-action@[0-9a-f]{40} # v5", backend)
    assert "type=sha,prefix=sha-" in backend
    assert "push: true" in backend
    assert re.search(r"aquasecurity/trivy-action@[0-9a-f]{40}", backend)
    assert "exit-code: '1'" in backend
    assert "az containerapp update" in backend
    assert "AZURE_CONTAINER_APP_NAME" in backend
    assert "deploy_to_azure" in backend
    assert "client-secret" not in backend
    assert "DATABASE_PASSWORD" not in backend
    assert "HLR_JWT_SECRET" not in backend
    assert "azurewebsites.net" not in backend


def test_frontend_workflow_keeps_the_existing_static_web_app_contract():
    frontend = (ROOT / ".github" / "workflows" / "deploy-frontend.yml").read_text(
        encoding="utf-8"
    )

    assert re.search(r"Azure/static-web-apps-deploy@[0-9a-f]{40} # v1", frontend)
    assert "VITE_API_BASE_URL: ${{ vars.HLR_BACKEND_URL }}" in frontend
    assert "app_location: frontend" in frontend
    assert "output_location: dist" in frontend


def test_runtime_secret_copy_uses_key_vault_without_writing_or_printing_values():
    script = (ROOT / "scripts" / "azure" / "copy_runtime_secrets_to_key_vault.sh").read_text(
        encoding="utf-8"
    )

    assert "az webapp config appsettings list" in script
    assert script.count("az keyvault secret set") == 2
    assert script.count("--output none") >= 2
    assert "Key Vault Secrets Officer" in script
    assert "> artifacts/" not in script
    assert "echo \"$DATABASE_PASSWORD\"" not in script
    assert "echo \"$JWT_SECRET\"" not in script


def test_operations_probe_is_scheduled_and_read_only():
    workflow = (ROOT / ".github" / "workflows" / "public-health.yml").read_text(
        encoding="utf-8"
    )

    assert "schedule:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "--read-only" in workflow
    assert "docs/deployment/public-urls.json" in workflow


def test_workflows_use_node_24_compatible_official_actions():
    workflows = list((ROOT / ".github" / "workflows").glob("*.yml"))
    text = "\n".join(path.read_text(encoding="utf-8") for path in workflows)

    assert "actions/checkout@v4" not in text
    assert "actions/setup-node@v4" not in text
    assert "actions/setup-python@v5" not in text
    assert re.search(r"actions/checkout@[0-9a-f]{40} # v6", text)
    assert re.search(r"actions/setup-node@[0-9a-f]{40} # v6", text)
    assert re.search(r"actions/setup-python@[0-9a-f]{40} # v6", text)


def test_pre_push_hook_runs_the_offline_final_verifier():
    hook = (ROOT / ".githooks" / "pre-push").read_text(encoding="utf-8")

    assert "scripts/final_verify.py --skip-live" in hook


def test_github_configuration_uses_environment_scoped_oidc():
    text = (ROOT / "scripts" / "azure" / "configure_github.sh").read_text(encoding="utf-8")

    assert "repo:eric861129/Habit-Life-RPG:environment:azure-demo" in text
    assert "api://AzureADTokenExchange" in text
    assert "gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN" in text
    assert "--sdk-auth" not in text
    assert '--role "Contributor"' not in text
    assert "Container Apps Contributor" in text
    assert "AZURE_CONTAINER_APP_NAME" in text
    assert "Website Contributor" not in text
    assert "custom_branch_policies" in text
    assert "deployment-branch-policies" in text
    assert '"name":"main"' in text
    assert '"type":"branch"' in text
