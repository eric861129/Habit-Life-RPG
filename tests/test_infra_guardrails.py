import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INFRA = ROOT / "infra"


def all_bicep_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in INFRA.rglob("*.bicep"))


def test_infrastructure_contains_only_approved_skus():
    text = all_bicep_text()

    assert "name: 'F1'" in text
    assert "tier: 'Free'" in text
    assert "useFreeLimit: true" in text
    assert "freeLimitExhaustionBehavior: 'AutoPause'" in text
    assert not re.search(r"name:\s*'(B1|S1|P[0-9]V[0-9])'", text)
    assert "BillOverUsage" not in text


def test_web_resources_enforce_transport_and_publish_guards():
    text = all_bicep_text()

    assert "httpsOnly: true" in text
    assert "minTlsVersion: '1.2'" in text
    assert "ftpsState: 'Disabled'" in text
    assert text.count("allow: false") >= 2


def test_database_is_capped_to_the_free_offer():
    text = all_bicep_text()

    assert "maxSizeBytes: 34359738368" in text
    assert "requestedBackupStorageRedundancy: 'Local'" in text
    assert "autoPauseDelay: 60" in text
    assert "minCapacity: json('0.5')" in text


def test_secrets_are_secure_parameters_and_never_outputs():
    text = all_bicep_text()
    output_lines = [line for line in text.splitlines() if line.strip().startswith("output ")]

    assert "@secure()\nparam sqlAdministratorPassword string" in text
    assert not any("password" in line.lower() or "secret" in line.lower() for line in output_lines)


def test_allowed_origins_are_explicitly_parameterized():
    text = all_bicep_text()

    assert "param allowedOrigins string" in text
    assert "HLR_ALLOWED_ORIGINS: allowedOrigins" in text
