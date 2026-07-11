from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EXAMPLE_VALUES = {
    "DATABASE_URL": "sqlite:///./habit_life_rpg.db",
    "HLR_JWT_SECRET": "replace-with-a-long-random-secret",
    "HLR_ACCESS_TOKEN_MINUTES": "60",
    "HLR_APP_TIMEZONE": "Asia/Taipei",
    "HLR_ALLOWED_ORIGINS": "http://localhost:5173,http://127.0.0.1:5173",
    "HLR_ENVIRONMENT": "development",
    "VITE_API_BASE_URL": "http://localhost:8000",
}


def load_environment_module():
    path = ROOT / "scripts" / "verify_environment.py"
    spec = spec_from_file_location("verify_environment", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_example() -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        result[key] = value
    return result


def test_example_environment_contains_the_public_configuration_contract():
    assert parse_example() == REQUIRED_EXAMPLE_VALUES


def test_example_environment_contains_no_real_secrets():
    values = parse_example()
    assert values["HLR_JWT_SECRET"] == "replace-with-a-long-random-secret"
    assert all("password" not in key.lower() for key in values)
    assert all("token" not in value.lower() for value in values.values())


def test_missing_keys_returns_only_blank_or_absent_required_values():
    module = load_environment_module()
    values = REQUIRED_EXAMPLE_VALUES | {"HLR_JWT_SECRET": ""}

    assert module.missing_keys(values) == ["HLR_JWT_SECRET"]


def test_validate_values_rejects_the_committed_secret_placeholder():
    module = load_environment_module()

    issues = module.validate_values(REQUIRED_EXAMPLE_VALUES)

    assert "HLR_JWT_SECRET must be replaced before running the app." in issues
