#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <subscription-id> <location> <parameters.local.json>" >&2
  exit 64
fi

SUBSCRIPTION_ID="$1"
LOCATION="$2"
PARAMETERS_FILE="$3"
DEPLOYMENT_NAME="hlr-book-v2-${LOCATION}"
DEPLOY_CONTAINER_APP="${HLR_DEPLOY_CONTAINER_APP:-NO}"
DEPLOYMENT_PARAMETERS=()

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
  echo "Set HLR_DEPLOY_CONFIRMED=YES only after reviewing the approved paid budget preflight and what-if." >&2
  exit 67
fi

if [[ "$DEPLOY_CONTAINER_APP" == "YES" ]]; then
  if [[ -z "${HLR_CONTAINER_IMAGE:-}" ]]; then
    echo "Set HLR_CONTAINER_IMAGE to an immutable GHCR SHA tag or digest." >&2
    exit 68
  fi

  if [[ ! "$HLR_CONTAINER_IMAGE" =~ ^ghcr\.io/eric861129/habit-life-rpg-api(@sha256:[0-9a-f]{64}|:sha-[0-9a-f]{7,40})$ ]]; then
    echo "HLR_CONTAINER_IMAGE must be an immutable image from the public book-demo package." >&2
    exit 68
  fi

  DEPLOYMENT_PARAMETERS+=(deployContainerApp=true "containerImage=$HLR_CONTAINER_IMAGE")
elif [[ "$DEPLOY_CONTAINER_APP" != "NO" ]]; then
  echo "HLR_DEPLOY_CONTAINER_APP must be YES or NO." >&2
  exit 68
fi

bash scripts/azure/preflight.sh "$SUBSCRIPTION_ID" "$LOCATION"
az account set --subscription "$SUBSCRIPTION_ID"

az deployment sub what-if \
  --name "$DEPLOYMENT_NAME" \
  --location "$LOCATION" \
  --template-file infra/main.bicep \
  --parameters "@$PARAMETERS_FILE" \
  "${DEPLOYMENT_PARAMETERS[@]}" \
  --only-show-errors

mkdir -p artifacts/azure
az deployment sub create \
  --name "$DEPLOYMENT_NAME" \
  --location "$LOCATION" \
  --template-file infra/main.bicep \
  --parameters "@$PARAMETERS_FILE" \
  "${DEPLOYMENT_PARAMETERS[@]}" \
  --query properties.outputs \
  --output json \
  --only-show-errors > artifacts/azure/deployment-outputs.local.json

RESOURCE_GROUP="$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.resourceGroupName.value --output tsv --only-show-errors)"
FRONTEND_HOST="$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.frontendHostname.value --output tsv --only-show-errors)"
APP_SERVICE_HOST="$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.backendHostname.value --output tsv --only-show-errors)"
WEBAPP_NAME="${APP_SERVICE_HOST%%.*}"
FRONTEND_ORIGIN="https://${FRONTEND_HOST}"

if [[ "$DEPLOY_CONTAINER_APP" == "YES" ]]; then
  BACKEND_HOST="$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.containerBackendHostname.value --output tsv --only-show-errors)"
else
  BACKEND_HOST="$APP_SERVICE_HOST"
fi

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

echo "Azure resources updated with approved paid budget settings. This deployment does not change the Static Web Apps resource or hostname."
echo "Candidate URLs: artifacts/azure/deployment-urls.json"
