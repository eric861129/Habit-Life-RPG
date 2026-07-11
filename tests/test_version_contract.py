import json
import tomllib
from pathlib import Path

import yaml

from backend.app.main import create_app


ROOT = Path(__file__).resolve().parents[1]


def test_final_release_versions_are_synchronized():
    python_project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    frontend = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
    lockfile = json.loads(
        (ROOT / "frontend" / "package-lock.json").read_text(encoding="utf-8")
    )
    openapi = yaml.safe_load((ROOT / "docs" / "openapi.yaml").read_text(encoding="utf-8"))

    assert {
        python_project["project"]["version"],
        frontend["version"],
        lockfile["version"],
        lockfile["packages"][""]["version"],
        openapi["info"]["version"],
        create_app().version,
    } == {"1.0.0"}
