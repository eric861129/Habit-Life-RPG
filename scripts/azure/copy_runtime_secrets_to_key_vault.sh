#!/usr/bin/env bash
set -euo pipefail

# Git Bash on Windows must not rewrite Azure resource IDs as local paths.
export MSYS_NO_PATHCONV=1

if [[ $# -ne 4 ]]; then
  echo "Usage: $0 <subscription-id> <resource-group> <source-webapp-name> <key-vault-name>" >&2
  exit 64
fi

SUBSCRIPTION_ID="$1"
RESOURCE_GROUP="$2"
SOURCE_WEBAPP_NAME="$3"
KEY_VAULT_NAME="$4"

command -v az >/dev/null 2>&1 || { echo "Azure CLI is required." >&2; exit 69; }

az account set --subscription "$SUBSCRIPTION_ID"

DATABASE_PASSWORD="$(az webapp config appsettings list \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SOURCE_WEBAPP_NAME" \
  --query "[?name=='DATABASE_PASSWORD'].value | [0]" \
  --output tsv \
  --only-show-errors)"

JWT_SECRET="$(az webapp config appsettings list \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SOURCE_WEBAPP_NAME" \
  --query "[?name=='HLR_JWT_SECRET'].value | [0]" \
  --output tsv \
  --only-show-errors)"

if [[ -z "$DATABASE_PASSWORD" || -z "$JWT_SECRET" ]]; then
  unset DATABASE_PASSWORD JWT_SECRET
  echo "The source Web App is missing one or more required runtime settings." >&2
  exit 65
fi

CURRENT_USER_OBJECT_ID="$(az ad signed-in-user show --query id --output tsv --only-show-errors)"
KEY_VAULT_ID="$(az keyvault show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$KEY_VAULT_NAME" \
  --query id \
  --output tsv \
  --only-show-errors)"

az role assignment create \
  --assignee-object-id "$CURRENT_USER_OBJECT_ID" \
  --assignee-principal-type User \
  --role "Key Vault Secrets Officer" \
  --scope "$KEY_VAULT_ID" \
  --output none \
  --only-show-errors

# Azure RBAC data-plane permissions can take a few seconds to propagate.
sleep 15

az keyvault secret set \
  --vault-name "$KEY_VAULT_NAME" \
  --name database-password \
  --value "$DATABASE_PASSWORD" \
  --output none \
  --only-show-errors

az keyvault secret set \
  --vault-name "$KEY_VAULT_NAME" \
  --name hlr-jwt-secret \
  --value "$JWT_SECRET" \
  --output none \
  --only-show-errors

unset DATABASE_PASSWORD JWT_SECRET

echo "The two runtime secrets were copied to Key Vault without printing their values."
