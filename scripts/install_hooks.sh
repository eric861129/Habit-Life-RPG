#!/usr/bin/env bash
set -euo pipefail

git config core.hooksPath .githooks
echo "HLR Git hooks enabled for this clone."
