#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <subscription-id> <location> <parameters.local.json>" >&2
  exit 64
fi

SUBSCRIPTION_ID="$1"
LOCATION="$2"
PARAMETERS_FILE="$3"
DEPLOYMENT_NAME="hlr-book-v2"

case "$PARAMETERS_FILE" in
  *.local.json) ;;
  *)
    echo "The parameters file must end with *.local.json so Git ignores its secrets." >&2
    exit 65
    ;;
esac

if [[ ! -f "$PARAMETERS_FILE" ]]; then
  echo "Parameters file not found: $PARAMETERS_FILE" >&2
  exit 66
fi

if [[ "${HLR_DEPLOY_CONFIRMED:-}" != "YES" ]]; then
  echo "Set HLR_DEPLOY_CONFIRMED=YES only after reviewing the zero-cost preflight and what-if." >&2
  exit 67
fi

bash scripts/azure/preflight.sh "$SUBSCRIPTION_ID" "$LOCATION"
az account set --subscription "$SUBSCRIPTION_ID"

az deployment sub what-if \
  --name "$DEPLOYMENT_NAME" \
  --location "$LOCATION" \
  --template-file infra/main.bicep \
  --parameters "@$PARAMETERS_FILE" \
  --only-show-errors

mkdir -p artifacts/azure
az deployment sub create \
  --name "$DEPLOYMENT_NAME" \
  --location "$LOCATION" \
  --template-file infra/main.bicep \
  --parameters "@$PARAMETERS_FILE" \
  --query properties.outputs \
  --output json \
  --only-show-errors > artifacts/azure/deployment-outputs.local.json

RESOURCE_GROUP="$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.resourceGroupName.value --output tsv --only-show-errors)"
FRONTEND_HOST="$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.frontendHostname.value --output tsv --only-show-errors)"
BACKEND_HOST="$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.backendHostname.value --output tsv --only-show-errors)"
WEBAPP_NAME="${BACKEND_HOST%%.*}"
FRONTEND_ORIGIN="https://${FRONTEND_HOST}"

az webapp config appsettings set \
  --resource-group "$RESOURCE_GROUP" \
  --name "$WEBAPP_NAME" \
  --settings "HLR_ALLOWED_ORIGINS=$FRONTEND_ORIGIN" \
  --output none \
  --only-show-errors

export FRONTEND_ORIGIN BACKEND_HOST
python3 - <<'PY'
import json
import os
from pathlib import Path

backend = f"https://{os.environ['BACKEND_HOST']}"
urls = {
    "frontend_url": os.environ["FRONTEND_ORIGIN"],
    "backend_url": backend,
    "health_live_url": f"{backend}/health/live",
    "health_ready_url": f"{backend}/health/ready",
    "docs_url": f"{backend}/docs",
}
Path("artifacts/azure/deployment-urls.json").write_text(
    json.dumps(urls, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

echo "Azure resources created with approved free settings. URLs: artifacts/azure/deployment-urls.json"
