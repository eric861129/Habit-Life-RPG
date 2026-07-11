# Azure 免費方案環境矩陣

本專案只允許以下 Azure 資源組合。任一項無法使用免費方案時，部署必須停止，不得自動改用付費 SKU。

| 層級 | Azure 服務 | 允許方案 | 超額行為 | SLA |
| --- | --- | --- | --- | --- |
| 前端 | Static Web Apps | Free | 停止提供服務，不改用付費方案 | 無 |
| 後端 | App Service Linux | F1 | 每日 CPU 配額用完後停止，不自動升級 | 無 |
| 資料庫 | Azure SQL Database | Free offer | 免費額度用完後 `AutoPause` 至下月 | 無 |

## 部署前檢查

```bash
az login
az account set --subscription <subscription-id>
bash scripts/azure/preflight.sh <subscription-id> <location>
```

`preflight.sh` 只執行帳號、Provider、區域與 SKU 查詢，不會建立或變更 Azure 資源。通過時，`artifacts/azure/preflight.json` 的 `allowed` 必須為 `true`，`estimated_monthly_cost` 必須為 `0`。

Azure SQL 免費方案是 General Purpose serverless 上的訂閱優惠；最終部署還必須在 what-if 與實際資源屬性中再次確認 `useFreeLimit: true` 與 `freeLimitExhaustionBehavior: AutoPause`。
