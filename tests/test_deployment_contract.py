from pathlib import Path

import pytest

from scripts.smoke_test import validate_urls


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


def test_deploy_script_requires_guards_before_resource_creation():
    text = (ROOT / "scripts" / "azure" / "deploy.sh").read_text(encoding="utf-8")

    preflight = text.index("preflight.sh")
    what_if = text.index("deployment sub what-if")
    create = text.index("deployment sub create")
    assert preflight < what_if < create
    assert "HLR_DEPLOY_CONFIRMED" in text
    assert "*.local.json" in text
    assert "BillOverUsage" not in text


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


def test_github_configuration_uses_environment_scoped_oidc():
    text = (ROOT / "scripts" / "azure" / "configure_github.sh").read_text(encoding="utf-8")

    assert "repo:eric861129/Habit-Life-RPG:environment:azure-demo" in text
    assert "api://AzureADTokenExchange" in text
    assert "gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN" in text
    assert "--sdk-auth" not in text
    assert '--role "Contributor"' not in text
    assert "Website Contributor" in text
