#!/usr/bin/env bash
set -euo pipefail

mkdir -p artifacts/azure
az bicep build --file infra/main.bicep --outfile artifacts/azure/main.json

if [[ -x .venv/bin/python ]]; then
  PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
else
  PYTHON_BIN="${PYTHON_BIN:-python3}"
fi

"$PYTHON_BIN" -m pytest tests/test_infra_guardrails.py -q
