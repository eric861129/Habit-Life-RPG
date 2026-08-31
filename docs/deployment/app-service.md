# Azure API Container Apps 部署與 App Service 回復

HLR API 的目標執行環境是 Azure Container Apps Consumption。Linux App Service `B1/Basic` 在 Phase 1 只作為切換後至少 48 小時的 rollback，不是長期固定計費方案。Static Web Apps resource 與公開 hostname 不會因 API 遷移而重建。

Container App 固定使用 0.5 vCPU／1 GiB、`minReplicas: 0`、`maxReplicas: 2` 與 HTTP concurrency 10。無流量時可 scale to zero，但第一個 request 可能遇到 cold start；這是降低 Demo 固定月費所接受的取捨。

## 建立資源

1. 將 `infra/main.parameters.example.json` 複製為以 `.local.json` 結尾的本機檔案。
2. 產生長隨機的 SQL 密碼與 JWT secret，只放在該本機檔。
3. 執行 paid-budget preflight 與 Bicep what-if，確認 Static Web Apps 仍是 `Free`、SQL 仍是 `Basic`，且只新增 Container Apps Consumption environment、managed identity、Key Vault 與必要 role assignment。
4. 設定 `HLR_DEPLOY_CONFIRMED=YES` 後才執行 `scripts/azure/deploy.sh`。

先以 `deployContainerApp=false` 建立平台資源，再執行 `scripts/azure/copy_runtime_secrets_to_key_vault.sh`。這個 script 只把既有 App Settings 中的 SQL password 與 JWT secret 直接複製到 Key Vault，不把值寫入檔案或輸出。

Container image 由 GitHub Actions 建置，發布到 public GHCR package，並以 commit SHA tag／digest 與雙層 Trivy scan 作為部署閘門。第一層完整列出所有 High／Critical vulnerability；第二層阻擋已有修正版但尚未修補的 High／Critical vulnerability。獨立的 secret scan 會阻擋任何 image secret finding。Public image 不包含 `.env`、password、JWT secret、Connection String、Azure credential 或 deployment token。

Container Apps 使用 `/health/live` 作為 startup／liveness probe、`/health/ready` 作為 readiness probe。`/health/live` 只確認 API process，不會因平台探測而額外查詢 SQL。

## 安全設定

- Container Apps 強制 HTTPS，不允許 insecure ingress。
- App Service rollback path 仍停用 FTP 與 SCM basic publishing credentials。
- CORS 只包含原 Static Web Apps origin。
- GitHub Actions 使用 protected environment + OIDC，不儲存 Azure client secret。
- OIDC service principal 只獲得目標 Container App 的 `Container Apps Contributor`。
- Runtime secret 由 user-assigned managed identity 讀取 Key Vault，不由 GitHub Actions 傳入。

## 驗收網址

- 建立後由 `containerBackendHostname` output 取得候選 API origin。
- `https://<container-host>/health/live`：進程活著即回應。
- `https://<container-host>/health/ready`：必須成功執行 Azure SQL `SELECT 1`。
- `https://<container-host>/docs`：FastAPI OpenAPI 互動文件。

既有 `azurewebsites.net` 網址在 48 小時觀察期仍提供 rollback。只有候選網址與完整 reader journey 驗收通過後，才能更新 `HLR_BACKEND_URL` 並重新部署前端；此動作只更新同一個 Static Web Apps resource 的內容，不改 hostname。

`scripts/smoke_test.py` 會針對冷啟動與暫時性 5xx 重試，但對永久性 4xx 立即失敗；它也會執行完整讀者業務旅程。
