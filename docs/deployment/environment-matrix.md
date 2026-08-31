# Azure 書籍 Demo 付費環境矩陣

本專案只允許下列 Azure 組合。preflight、Bicep guardrails 或 what-if 任一項不符就停止部署，不得自動提高 SKU 或增加 instance。

| 層級 | Azure 服務 | 允許方案 | 成本／限制 |
| --- | --- | --- | --- |
| 前端 | Static Web Apps | Free | 保持免費 production environment |
| 後端 | Azure Container Apps | Consumption，0–2 replicas | 0.5 vCPU／1 GiB；無流量 scale to zero，超過每月 free grant 後按用量計費 |
| 回復 | App Service Linux | B1，capacity 1 | 只在切換後至少 48 小時保留；未另行確認前不停止或刪除 |
| 資料庫 | Azure SQL Database | Basic 5 DTU，2 GB | 約 US$4.90／月，無法暫停 |
| 機密 | Azure Key Vault | Standard | 只保存 SQL password 與 JWT secret；Container App 以 managed identity 讀取 |
| 成本治理 | Resource Group Budget | Monthly US$30 | 50%、80%、100% Actual 與 100% Forecasted 通知 |
| 通知 | Azure Monitor Action Group | Subscription Owner role | 只通知，不執行自動停機或刪除 |

## 部署前檢查

```bash
az login --tenant ChiYuAzure.onmicrosoft.com
az account set --subscription <subscription-id>
bash scripts/azure/preflight.sh <subscription-id> westus2
```

`preflight.sh` 只查詢帳號、Provider、區域、SKU 與 Azure Retail Prices，不會建立或變更 Azure 資源。通過時，`artifacts/azure/preflight.json` 必須符合：

- `allowed: true`
- 過渡期 `estimated_monthly_cost_usd` 不超過 `20`；此值包含仍保留的 B1 與 SQL Basic 固定月費，不把 Container Apps free grant 誤算成保證
- `budget_amount_usd` 等於 `30`
- `container_apps_consumption`、`key_vault_available`、`managed_identity_available`、`app_service_b1_linux`、`azure_sql_basic`、`static_web_apps_free` 全部為 `true`

Phase 1 what-if 只允許新增 Container Apps Consumption environment、user-assigned managed identity、Key Vault 與必要的 Key Vault reader role；既有 SWA、B1、SQL Basic、Action Group 與 Budgets 不得 replace 或 delete。Container App 本體要等 GHCR SHA image 與 Key Vault secrets 就緒後才建立。任何額外固定付費服務、Log Analytics workspace、ACR、較高 SKU 或更多 replica 都必須停止。
