from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_ci_runs_backend_contract_and_optional_frontend_gates():
    workflow_path = ROOT / ".github" / "workflows" / "ci.yml"
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    assert set(workflow["jobs"]) == {"backend", "contract", "frontend"}
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


def test_ci_uses_supported_book_runtime_versions():
    text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert 'python-version: "3.12"' in text
    assert 'node-version: "22"' in text
