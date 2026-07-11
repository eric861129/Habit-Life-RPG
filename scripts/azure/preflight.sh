#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <subscription-id> <location>" >&2
  exit 64
fi

if ! command -v az >/dev/null 2>&1; then
  echo "Azure CLI is required. Install it before running the preflight." >&2
  exit 69
fi

python3 scripts/azure/check_free_skus.py "$1" "$2"
