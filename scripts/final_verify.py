from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def verification_commands(*, include_live: bool) -> list[list[str]]:
    python = sys.executable
    commands = [
        [python, "-m", "ruff", "check", "backend", "tests", "scripts"],
        [python, "-m", "pytest", "-q"],
        [python, "scripts/verify_openapi.py"],
        ["npm", "--prefix", "frontend", "test", "--", "--run"],
        ["npm", "--prefix", "frontend", "run", "build"],
    ]
    if include_live:
        commands.append(
            [
                python,
                "scripts/smoke_test.py",
                "--urls",
                "docs/deployment/public-urls.json",
                "--read-only",
            ]
        )
    return commands


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the complete HLR release verification.")
    parser.add_argument(
        "--skip-live",
        action="store_true",
        help="omit the public Azure probe for offline or pre-push verification",
    )
    args = parser.parse_args()

    for command in verification_commands(include_live=not args.skip_live):
        print(f"$ {shlex.join(command)}", flush=True)
        subprocess.run(command, cwd=ROOT, check=True)
    print("HLR final verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
