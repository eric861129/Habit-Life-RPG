# Azure App Service 後端部署

HLR API 使用 Linux App Service `F1` 免費方案。此方案適合書籍示範與學習，沒有 SLA，且受每日 CPU 配額限制；冷啟動或配額用完時可能暫時無法回應。

## 建立資源

1. 將 `infra/main.parameters.example.json` 複製為以 `.local.json` 結尾的本機檔案。
2. 產生長隨機的 SQL 密碼與 JWT secret，只放在該本機檔。
3. 執行免費方案 preflight 與 Bicep what-if，確認只有 `F1`、`Free` 與 SQL free offer。
4. 設定 `HLR_DEPLOY_CONFIRMED=YES` 後才執行 `scripts/azure/deploy.sh`。

App Service 以 Python 3.12 啟動，先執行 Alembic migration，再啟動 Uvicorn。`DATABASE_PASSWORD`、`HLR_JWT_SECRET` 等設定只存在 App Settings，不出現在 Git 或 Bicep output。

## 安全設定

- 強制 HTTPS 與 TLS 1.2。
- 停用 FTP 與 SCM basic publishing credentials。
- CORS 只包含實際 Static Web Apps origin。
- GitHub Actions 使用 environment-scoped OIDC，不儲存 Azure client secret。
- OIDC service principal 只獲得單一 Web App 的 `Website Contributor`。

## 驗收網址

- <https://hlr-eric861129-v2-api.azurewebsites.net>：公開服務首頁。
- <https://hlr-eric861129-v2-api.azurewebsites.net/health/live>：進程活著即回應。
- <https://hlr-eric861129-v2-api.azurewebsites.net/health/ready>：必須成功執行 Azure SQL `SELECT 1`。
- <https://hlr-eric861129-v2-api.azurewebsites.net/docs>：FastAPI OpenAPI 互動文件。

`scripts/smoke_test.py` 會針對冷啟動與暫時性 5xx 重試，但對永久性 4xx 立即失敗；它也會執行完整讀者業務旅程。
