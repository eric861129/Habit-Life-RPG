#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 5 ]]; then
  echo "Usage: $0 <subscription-id> <resource-group> <webapp-name> <static-site-name> <backend-url>" >&2
  exit 64
fi

SUBSCRIPTION_ID="$1"
RESOURCE_GROUP="$2"
WEBAPP_NAME="$3"
STATIC_SITE_NAME="$4"
BACKEND_URL="$5"
REPOSITORY="eric861129/Habit-Life-RPG"
ENVIRONMENT="azure-demo"
APP_DISPLAY_NAME="hlr-book-github-actions"
FEDERATED_NAME="github-azure-demo"

command -v az >/dev/null 2>&1 || { echo "Azure CLI is required." >&2; exit 69; }
command -v gh >/dev/null 2>&1 || { echo "GitHub CLI is required." >&2; exit 69; }

az account set --subscription "$SUBSCRIPTION_ID"
TENANT_ID="$(az account show --query tenantId --output tsv --only-show-errors)"

CLIENT_ID="$(az ad app list --display-name "$APP_DISPLAY_NAME" --query '[0].appId' --output tsv --only-show-errors)"
if [[ -z "$CLIENT_ID" ]]; then
  CLIENT_ID="$(az ad app create --display-name "$APP_DISPLAY_NAME" --query appId --output tsv --only-show-errors)"
fi

SP_OBJECT_ID="$(az ad sp list --filter "appId eq '$CLIENT_ID'" --query '[0].id' --output tsv --only-show-errors)"
if [[ -z "$SP_OBJECT_ID" ]]; then
  SP_OBJECT_ID="$(az ad sp create --id "$CLIENT_ID" --query id --output tsv --only-show-errors)"
fi

mkdir -p artifacts/azure
cat > artifacts/azure/github-federated-credential.local.json <<JSON
{
  "name": "$FEDERATED_NAME",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:eric861129/Habit-Life-RPG:environment:azure-demo",
  "description": "HLR Azure deployment from the protected GitHub environment",
  "audiences": ["api://AzureADTokenExchange"]
}
JSON

EXISTING_CREDENTIAL="$(az ad app federated-credential list --id "$CLIENT_ID" --query "[?name=='$FEDERATED_NAME'].name | [0]" --output tsv --only-show-errors)"
if [[ -z "$EXISTING_CREDENTIAL" ]]; then
  az ad app federated-credential create \
    --id "$CLIENT_ID" \
    --parameters artifacts/azure/github-federated-credential.local.json \
    --output none \
    --only-show-errors
fi

WEBAPP_ID="$(az webapp show --resource-group "$RESOURCE_GROUP" --name "$WEBAPP_NAME" --query id --output tsv --only-show-errors)"
az role assignment create \
  --assignee-object-id "$SP_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Website Contributor" \
  --scope "$WEBAPP_ID" \
  --output none \
  --only-show-errors

gh api --method PUT "repos/$REPOSITORY/environments/$ENVIRONMENT" >/dev/null
gh variable set AZURE_CLIENT_ID --repo "$REPOSITORY" --env "$ENVIRONMENT" --body "$CLIENT_ID"
gh variable set AZURE_TENANT_ID --repo "$REPOSITORY" --env "$ENVIRONMENT" --body "$TENANT_ID"
gh variable set AZURE_SUBSCRIPTION_ID --repo "$REPOSITORY" --env "$ENVIRONMENT" --body "$SUBSCRIPTION_ID"
gh variable set AZURE_RESOURCE_GROUP --repo "$REPOSITORY" --env "$ENVIRONMENT" --body "$RESOURCE_GROUP"
gh variable set AZURE_WEBAPP_NAME --repo "$REPOSITORY" --env "$ENVIRONMENT" --body "$WEBAPP_NAME"
gh variable set HLR_BACKEND_URL --repo "$REPOSITORY" --env "$ENVIRONMENT" --body "$BACKEND_URL"

STATIC_TOKEN="$(az staticwebapp secrets list --resource-group "$RESOURCE_GROUP" --name "$STATIC_SITE_NAME" --query properties.apiKey --output tsv --only-show-errors)"
printf '%s' "$STATIC_TOKEN" | gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN \
  --repo "$REPOSITORY" \
  --env "$ENVIRONMENT"
unset STATIC_TOKEN

echo "GitHub environment '$ENVIRONMENT' configured with OIDC and a masked Static Web Apps token."
