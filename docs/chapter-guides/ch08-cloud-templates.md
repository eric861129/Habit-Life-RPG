# 第 8 章：Azure 雲端實戰

`chapter/08-deployment` 將第 7 章 MVP 部署到零月費防線內的 Azure 示範環境。

## 零成本防線

- Static Web Apps 只允許 Free。
- Linux App Service 只允許 F1。
- Azure SQL 必須是 `useFreeLimit: true` 與 `freeLimitExhaustionBehavior: AutoPause`。
- preflight 任一欄為 false，或估計月費不為 0，就停止部署。
- Bicep 守門測試明確拒絕 B1、S1 與 Premium SKU。
- 同一訂閱若已有 SQL free offer，所有免費資料庫必須使用相同區域；preflight 會在建立資源前阻擋不相容區域。本次部署使用 `westus2`。

## 建立與部署

```bash
bash scripts/azure/preflight.sh <subscription-id> <location>
bash scripts/azure/validate_infra.sh
HLR_DEPLOY_CONFIRMED=YES bash scripts/azure/deploy.sh \
  <subscription-id> <location> artifacts/azure/main.parameters.local.json
```

資源建立後，執行 `scripts/azure/configure_github.sh` 建立 `azure-demo` GitHub Environment、OIDC 憑證與被遮罩的 SWA Token。後端與前端 workflow 都必須先通過各自的 test job。

## 公開驗收

`artifacts/azure/deployment-urls.json` 保存不含祕密的公開網址，並由以下指令驗證：

```bash
python scripts/smoke_test.py --urls artifacts/azure/deployment-urls.json
```

公開網址與實際 smoke test 結果只會在資源成功建立後寫入；未部署前不使用假 URL 充當成品。

## 已驗證公開網址

- 前端：<https://victorious-dune-0ad92d11e.7.azurestaticapps.net>
- API：<https://hlr-eric861129-v2-api.azurewebsites.net>
- API 文件：<https://hlr-eric861129-v2-api.azurewebsites.net/docs>
- Liveness：<https://hlr-eric861129-v2-api.azurewebsites.net/health/live>
- Readiness：<https://hlr-eric861129-v2-api.azurewebsites.net/health/ready>

`scripts/smoke_test.py` 已驗證所有網址為 HTTP 200，並完成註冊、登入、建立與列出 Habit、Check-in、同日重複 Check-in 409、獎勵資料與封存。SQL Server 契約測試另涵蓋 Unicode `NVARCHAR`、Boolean `BIT` 查詢與多重 cascade path 防護。

示範帳號為 `book-demo`，密碼為 `HabitLifeRPG2026!`。這組憑證是公開教材的一部分，不是祕密；讀者不可在共享帳號輸入個人資料。
