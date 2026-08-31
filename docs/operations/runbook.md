# HLR 維運手冊

## 服務清冊

- 前端：<https://victorious-dune-0ad92d11e.7.azurestaticapps.net>
- API（切換前／48 小時 rollback）：<https://hlr-eric861129-v2-api.azurewebsites.net>
- Readiness：<https://hlr-eric861129-v2-api.azurewebsites.net/health/ready>
- API 文件：<https://hlr-eric861129-v2-api.azurewebsites.net/docs>
- Azure resource group：`hlr-eric861129-v2-rg`
- GitHub Environment：`azure-demo`

## 事故處理順序

1. 執行唯讀 smoke，保存失敗網址與 HTTP 狀態。
2. Container Apps scale-from-zero 的第一個 request 若逾時或 5xx，等待 2 分鐘後只重試一次，區分 cold start 與持續故障。
3. `/health/live` 失敗時查看 Container App provisioning state、active revision、replica restart 與即時 console stream；未設定 Log Analytics，不應假設有長期 log retention。
4. live 成功但 ready 503 時，查看 Azure SQL status、firewall、Key Vault reference 與五個必要 environment variable 名稱是否齊全；不得輸出設定值。
5. 前端失敗但 API 正常時，查看 Static Web Apps production environment 與最近一次 frontend workflow。
6. 修復後先跑唯讀 smoke，再跑一次完整 reader journey；完整模式會建立一次性測試帳號。

## 常用命令

```bash
az webapp show \
  --resource-group hlr-eric861129-v2-rg \
  --name hlr-eric861129-v2-api \
  --query '{state:state,host:defaultHostName}'

az webapp log deployment list \
  --resource-group hlr-eric861129-v2-rg \
  --name hlr-eric861129-v2-api

az containerapp show \
  --resource-group hlr-eric861129-v2-rg \
  --name hlr-eric861129-v2-api-ca \
  --query '{state:properties.provisioningState,host:properties.configuration.ingress.fqdn}'

az containerapp revision list \
  --resource-group hlr-eric861129-v2-rg \
  --name hlr-eric861129-v2-api-ca \
  --query '[].{name:name,active:properties.active,healthy:properties.healthState}'

python scripts/smoke_test.py \
  --urls docs/deployment/public-urls.json \
  --read-only
```

48 小時觀察期間需要回復時，先把 GitHub Environment 的 `HLR_BACKEND_URL` 改回既有 App Service origin，再重新執行 frontend workflow。只有確認前端已回復後，才處理失敗的 Container App revision；不要重建 Static Web Apps resource。

舊 App Service 如需重新啟動，只操作這個明確資源：

```bash
az webapp restart \
  --resource-group hlr-eric861129-v2-rg \
  --name hlr-eric861129-v2-api
```

## 部署與回復

後端 workflow 必須先通過 test、image build 與 Trivy scan，並以 SHA tag／digest 部署。前端 workflow 必須先通過 test。部署失敗時，不變更 replica 或 SQL SKU；Container App 使用 single active revision，可重新部署上一個已驗證 image digest。不得直接 force-push 章節分支或改寫既有 Tag。

任何基礎設施變更前重新執行：

```bash
bash scripts/azure/preflight.sh <subscription-id> westus2
bash scripts/azure/validate_infra.sh
```

只有 preflight 的所有 guard 為 true、過渡期 `estimated_monthly_cost_usd` 不超過 US$20、IaC Budget 為 NT$960、Alert Budget 為 NT$640，且 Phase 1 what-if 只新增 Consumption environment、managed identity、Key Vault、Key Vault reader role 與核准的 Container App 時才能繼續。Azure Budget 金額使用訂閱帳務幣別 TWD，US$30 只代表政策目標。

Budget 告警不會停止服務。Container App 的 `minReplicas: 0` 已是閒置最低用量；SQL Basic 無法暫停，禁止用刪除資料庫當作自動停損。B1 停用或降級仍須在 48 小時觀察完成後另行確認。

## 示範資料與隱私

`book-demo` 是公開共享帳號，不保證內容穩定。讀者自己的帳號與 Habit 不得被維運腳本自動刪除。需要處理資料刪除請求時，先確認請求者能登入該帳號，再以最小範圍處理；不得要求或記錄讀者密碼。詳見 `docs/operations/privacy-policy.md`。
