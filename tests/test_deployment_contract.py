from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError

import pytest

from scripts.smoke_test import api_request, validate_urls, verify_reader_journey


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
        "profile": 200,
        "register": 201,
    }
    assert len(calls) == 7


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


def test_deploy_script_requires_guards_before_resource_creation():
    text = (ROOT / "scripts" / "azure" / "deploy.sh").read_text(encoding="utf-8")

    preflight = text.index("preflight.sh")
    what_if = text.index("deployment sub what-if")
    create = text.index("deployment sub create")
    assert preflight < what_if < create
    assert "HLR_DEPLOY_CONFIRMED" in text
    assert "*.local.json" in text
    assert "BillOverUsage" not in text


def test_deploy_script_scopes_subscription_deployment_name_to_location():
    text = (ROOT / "scripts" / "azure" / "deploy.sh").read_text(encoding="utf-8")

    assert 'DEPLOYMENT_NAME="hlr-book-v2-${LOCATION}"' in text


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
