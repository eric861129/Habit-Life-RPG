import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_ci_runs_backend_contract_and_optional_frontend_gates():
    workflow_path = ROOT / ".github" / "workflows" / "ci.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    assert set(workflow["jobs"]) == {"backend", "contract", "frontend", "secret-scan"}
    text = workflow_path.read_text(encoding="utf-8")
    for command in (
        "python -m pip install -e \".[dev]\"",
        "python -m ruff check backend tests scripts",
        "python -m pytest -q",
        "python scripts/verify_openapi.py",
        "npm ci",
        "npm test -- --run",
        "npm run build",
    ):
        assert command in text
    assert "frontend/package-lock.json" in text
    assert "gitleaks/gitleaks-action@e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e" in text


def test_ci_uses_supported_book_runtime_versions():
    text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert 'python-version: "3.12"' in text
    assert 'node-version: "22"' in text


def test_all_external_actions_are_pinned_to_full_commit_sha():
    workflows = ROOT / ".github" / "workflows"

    for workflow_path in workflows.glob("*.yml"):
        text = workflow_path.read_text(encoding="utf-8")
        action_refs = re.findall(r"\buses:\s*([^\s#]+)", text)

        for action_ref in action_refs:
            assert re.fullmatch(r"[^@]+@[0-9a-f]{40}", action_ref), (
                f"{workflow_path.name} must pin {action_ref} to a full commit SHA"
            )
