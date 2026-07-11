# HLR 維運手冊

## 服務清冊

- 前端：<https://victorious-dune-0ad92d11e.7.azurestaticapps.net>
- API：<https://hlr-eric861129-v2-api.azurewebsites.net>
- Readiness：<https://hlr-eric861129-v2-api.azurewebsites.net/health/ready>
- API 文件：<https://hlr-eric861129-v2-api.azurewebsites.net/docs>
- Azure resource group：`hlr-eric861129-v2-rg`
- GitHub Environment：`azure-demo`

## 事故處理順序

1. 執行唯讀 smoke，保存失敗網址與 HTTP 狀態。
2. 若回應 403 stopped page，確認 Web App state；若首次逾時或 5xx，等待 2 分鐘後只重試一次，以容納 F1／SQL 冷啟動。
3. `/health/live` 失敗時查看 App Service container log 與最新 deployment status。
4. live 成功但 ready 503 時，查看 Azure SQL status、free amount remaining、firewall 與四個 `DATABASE_*` App Settings 是否齊全；不得輸出設定值。
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

python scripts/smoke_test.py \
  --urls docs/deployment/public-urls.json \
  --read-only
```

需要重新啟動時，只操作明確的 Web App：

```bash
az webapp restart \
  --resource-group hlr-eric861129-v2-rg \
  --name hlr-eric861129-v2-api
```

## 部署與回復

後端與前端 workflow 必須先通過 test job。部署失敗時，不變更 SKU；確認上一個健康版本後，從對應 `book-v2-chXX-*` Tag 建立修復分支，再透過相同 workflow 部署。不得直接 force-push 章節分支或改寫既有 Tag。

任何基礎設施變更前重新執行：

```bash
bash scripts/azure/preflight.sh <subscription-id> westus2
bash scripts/azure/validate_infra.sh
```

只有 preflight 的所有 guard 為 true、estimated monthly cost 為 0，且 what-if 沒有付費 SKU 時才能繼續。SQL free-limit exhaustion behavior 必須維持 `AutoPause`。

## 示範資料與隱私

`book-demo` 是公開共享帳號，不保證內容穩定。讀者自己的帳號與 Habit 不得被維運腳本自動刪除。需要處理資料刪除請求時，先確認請求者能登入該帳號，再以最小範圍處理；不得要求或記錄讀者密碼。詳見 `docs/operations/privacy-policy.md`。
