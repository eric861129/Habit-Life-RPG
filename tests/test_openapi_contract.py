from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest
import yaml

from backend.app.main import create_app


ROOT = Path(__file__).resolve().parents[1]


def load_verifier():
    path = ROOT / "scripts" / "verify_openapi.py"
    spec = spec_from_file_location("verify_openapi", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runtime_openapi_matches_committed_operation_signatures():
    verifier = load_verifier()
    runtime = create_app().openapi()
    committed = yaml.safe_load((ROOT / "docs" / "openapi.yaml").read_text(encoding="utf-8"))

    assert verifier.operation_signatures(runtime) == verifier.operation_signatures(committed)


def test_openapi_verifier_reports_human_readable_differences():
    verifier = load_verifier()
    left = {"paths": {"/health/live": {"get": {"responses": {"200": {}}}}}}
    right = {"paths": {"/health/live": {"get": {"responses": {"503": {}}}}}}

    differences = verifier.compare_contracts(left, right)

    assert differences == [
        "GET /health/live: runtime responses ['200'] != committed responses ['503']"
    ]


def test_openapi_loader_rejects_duplicate_yaml_keys():
    verifier = load_verifier()

    with pytest.raises(ValueError, match="Duplicate YAML key: '200'"):
        verifier.load_contract("responses:\n  '200': ok\n  '200': duplicate\n")
