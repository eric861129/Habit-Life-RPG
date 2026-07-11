from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_KEYS = (
    "DATABASE_URL",
    "HLR_JWT_SECRET",
    "HLR_ACCESS_TOKEN_MINUTES",
    "HLR_APP_TIMEZONE",
    "HLR_ALLOWED_ORIGINS",
    "HLR_ENVIRONMENT",
    "VITE_API_BASE_URL",
)
SECRET_PLACEHOLDER = "replace-with-a-long-random-secret"


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid environment line: {raw_line}")
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def missing_keys(values: dict[str, str]) -> list[str]:
    return [key for key in REQUIRED_KEYS if not values.get(key, "").strip()]


def validate_values(values: dict[str, str]) -> list[str]:
    issues = [f"{key} is required." for key in missing_keys(values)]
    if values.get("HLR_JWT_SECRET") == SECRET_PLACEHOLDER:
        issues.append("HLR_JWT_SECRET must be replaced before running the app.")

    token_minutes = values.get("HLR_ACCESS_TOKEN_MINUTES", "")
    if token_minutes and (not token_minutes.isdigit() or int(token_minutes) <= 0):
        issues.append("HLR_ACCESS_TOKEN_MINUTES must be a positive integer.")

    origins = [item.strip() for item in values.get("HLR_ALLOWED_ORIGINS", "").split(",")]
    if any(origin and not origin.startswith(("http://", "https://")) for origin in origins):
        issues.append("HLR_ALLOWED_ORIGINS must contain HTTP or HTTPS origins.")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate local Habit Life RPG settings.")
    parser.add_argument("--file", type=Path, default=Path(".env"))
    args = parser.parse_args(argv)

    if not args.file.exists():
        print(f"Environment file not found: {args.file}")
        print("Create it with: cp .env.example .env")
        return 1

    try:
        values = parse_env_file(args.file)
    except ValueError as error:
        print(error)
        return 1

    issues = validate_values(values)
    if issues:
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(f"Environment contract is valid: {args.file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
