# HLR 書籍 Demo Azure 付費服務規劃

> 狀態：Demo Phase 1 實作中／Container Apps 並行遷移，既有 B1 尚未停用
> 盤點日期：2026-08-26
> 適用範圍：`hlr-eric861129-v2-rg` 內的書籍 Demo 服務
> 執行狀態：B1、SQL Basic、NT$960 Budget、NT$640 Alert Budget 與告警已套用成功；兩個 Budget 分別約為 US$30 與 US$20。公開功能與 20-user 基準通過，但 50-user 上市容量門檻未通過

## 0. 2026-08-31 核准的 Demo Phase 1 變更

本節取代本文後續章節對「B1 是長期 API 方案」的建議；後續章節保留為 2026-08-26 的實作與量測紀錄。正式產品 API／Web repository 不在本次範圍。

核准後的目標是把書籍 Demo API 從固定計費的 App Service B1 遷移到 Azure Container Apps Consumption，同時把讀者已取得的前端網址視為不可變契約：

- `hlr-eric861129-v2-web` 保留原 Static Web Apps Free resource，公開 hostname `victorious-dune-0ad92d11e.7.azurestaticapps.net` 不重建、不更名。
- 新 API 使用 `hlr-eric861129-v2-api-ca`，`minReplicas: 0`、`maxReplicas: 2`、每個 replica 0.5 vCPU／1 GiB，HTTP concurrency 10。比原先 0.25 vCPU／0.5 GiB 多保留記憶體，是依 B1 負載測試曾出現高記憶體峰值所做的保守調整。
- Azure SQL Database 保持 Basic 5 DTU／2 GB，不做資料庫轉層、schema migration 或資料搬移。
- Runtime 的 SQL 密碼與 JWT secret 從既有 App Settings 安全複製到 Azure Key Vault；Container App 以 user-assigned managed identity 讀取，不把值放進 Bicep、GitHub Variables、workflow、image 或 log。
- Container image 發布到與 Public repository 關聯的 GHCR package。image 不包含機密，部署只接受 commit SHA tag 或 digest。Trivy 先完整列出所有 High／Critical vulnerability，再阻擋已有修正版但尚未修補的 High／Critical vulnerability；任何 image secret finding 一律阻擋部署。
- GitHub Actions 延續 environment-scoped OIDC，不建立 Azure client secret；部署 identity 只取得目標 Container App 的 `Container Apps Contributor`。
- 新 API 必須先通過 `/health/live`、`/health/ready` 與完整 reader journey，之後才更新 GitHub Environment 的 `HLR_BACKEND_URL` 並重新部署同一個 Static Web Apps resource。
- App Service B1 在切換後至少保留 48 小時作為 rollback。觀察完成前不停止、不降級、不刪除；後續停用需要另一次明確確認。

這個 Demo 沒有正式 C# API 的 `ReviewSealingHostedService`，因此不建立每日 Container Apps Job。本文早期對背景服務的假設已由 Azure runtime 與 Public repository 原始碼確認為不適用。

Container Apps 的 Consumption 計費仍是用量制，不是硬性 US$30 spending limit。`minReplicas: 0` 可在無流量時 scale to zero，現有 NT$640／NT$960 Budget 與通知保持不變；SQL Basic 仍是預期主要固定月費。

網址邊界需清楚區分：前端 Static Web Apps hostname 保持不變；API 的 `azurewebsites.net` hostname 會在 B1 最終停用後失效。書稿若只公開前端 Demo URL，不受影響；若正文也印出 API URL，必須在停用 B1 前另外決定是否保留 F1 redirect／proxy，不能假設 API hostname 也會自動延續。

## 1. 決策摘要

本計畫建議用最低固定付費組合恢復 Demo 可用性，並將一般月費控制在 US$15–20：

- Static Web App 保持 `Free`。
- API App Service Plan 從 Linux `F1/Free` 升級為 `B1/Basic`，固定一個執行個體。
- Azure SQL Database 從 Free General Purpose Serverless 改為 `Basic` 5 DTU。
- 在資源群組保留每月 NT$960 Budget 與原四組通知，另建每月 NT$640 告警 Budget。Azure Budget 以訂閱帳務幣別 TWD 評估，兩者分別約為 US$30 與 US$20。
- IaC 與測試鎖定 B1、SQL Basic、單一執行個體，避免部署流程誤用更高 SKU。
- 第一階段不做自動停機或刪除資源。Azure Pay-As-You-Go 沒有可自訂的硬性 US$30 spending limit，Budget 也不會停止服務。

預估固定月費約 US$17.31–18.04，保留約 US$11.96–12.69 的預算緩衝。價格仍應在部署當天以 Azure Portal 與 Retail Prices API 重新確認。

## 2. 目標與非目標

### 2.1 目標

1. 排除 App Service F1 每日 CPU 配額造成的 API 停機。
2. 排除 Azure SQL 免費 vCore 額度用完後暫停至下月的問題。
3. 將固定資源月費控制在 US$20 內。
4. 用 US$30 月預算、告警與 IaC guardrails 降低意外超支風險。
5. 保留目前公開網址、資料與 GitHub 部署流程。
6. 在新書推出前用實際負載測試確認最低付費層是否足夠。

### 2.2 非目標

- 不改寫已出版的 chapter branches、tags 或 releases。
- 不把新產品 API／Web repository 併回書籍 Demo。
- 不新增 Log Analytics、Application Insights、Front Door、Redis、CDN 或其他可能增加固定費用的服務。
- 不承諾 B1 + SQL Basic 可承受未定義的「大量流量」；容量必須由負載測試證明。
- 不建立自動刪除 SQL Database、Resource Group 或讀者資料的流程。

## 3. 現況盤點

### 3.1 Azure 資源

| 資源 | 目前方案／狀態 | 已確認問題 |
| --- | --- | --- |
| `hlr-eric861129-v2-web` | Static Web Apps Free，前端可回應 HTTP 200 | 暫無需調整 |
| `hlr-eric861129-v2-api` | Linux App Service F1 | Portal 顯示已超出配額；公開 API 曾回應 403 stopped page，最新探測亦出現 503／逾時 |
| `hlr-eric861129-v2-plan` | F1/Free，單一執行個體 | F1 只有每日 60 CPU 分鐘，超額後服務停止至配額重設 |
| `habit-life-rpg` | Azure SQL Free General Purpose Serverless，Paused | 當月免費額度剩餘 `0 vCore seconds`，免費額度用完後停至下月 |
| `hlr-eric861129-v2-sql` | Azure SQL logical server | 保持現況 |

資源群組目前共有 5 個資源，區域皆為 `West US 2`。

### 3.2 成本管理現況

- 資源群組目前沒有任何 Budget。
- 資源群組目前沒有任何費用警示。
- 訂閱為 Pay-As-You-Go，無法設定自訂硬性 spending limit。
- Azure Cost Management 成本資料通常延遲 8–24 小時，因此告警不等同即時計費斷路器。

### 3.3 Repository 與 IaC 現況

實際 Azure Demo 的 IaC 位於書籍示範 repository，不在後續產品 repository：

- 書籍 Demo：`D:\MySelf\LR\Habit-Life-RPG`
- 後續產品 API：`D:\MySelf\LR\Habit-Life-RPG-Api`
- 後續產品 Web：`D:\MySelf\LR\Habit-Life-RPG-Web`

目前 IaC 明確鎖定零成本：

- `infra/modules/app-service.bicep`：`F1/Free`、capacity 1、`alwaysOn: false`。
- `infra/modules/sql-free-database.bicep`：Free General Purpose Serverless、`AutoPause`、最大 32 GB。
- `infra/main.bicep`：tag 為 `costPolicy: zero-cost-only`。
- `tests/test_infra_guardrails.py`：拒絕 B1 與其他付費 SKU。
- `scripts/azure/check_free_skus.py`：只接受月費為 0 的 preflight。
- `scripts/azure/deploy.sh`：preflight、what-if、人工確認後才部署。

目前 API 使用單一 Uvicorn process；SQLAlchemy 沒有自訂 pool size，會使用預設連線池。這也是正式宣稱可承受新書流量前必須負載測試的原因。

## 4. 建議目標架構

| 層級 | Azure 服務 | 目標方案 | 設定上限 | 理由 |
| --- | --- | --- | --- | --- |
| 前端 | Static Web Apps | Free | 保持單一 production environment | 目前正常，靜態內容不需要升級 |
| API | App Service Linux | Basic B1 | 1 vCPU、1.75 GB RAM、1 instance | 移除 F1 CPU 日配額，維持最低固定費用 |
| 資料庫 | Azure SQL Database | Basic 5 DTU | 2 GB、Local backup redundancy | 現有資料約 22 MB，容量足夠，費用固定 |
| 成本治理 | Cost Management Budget | Monthly NT$960，約 US$30 | 資源群組範圍 | 提供實際與預測費用通知 |
| 通知 | Azure Monitor Action Group | Subscription Owner role | 僅通知，不執行刪除 | 避免在公開 repository 寫入個人 Email |

API 的 App Service 設定預計同步調整：

- `alwaysOn: true`，減少新書公開期間的冷啟動。
- `healthCheckPath: /health/live`，平台健康檢查不主動查詢資料庫。
- `httpsOnly: true`、TLS 1.2、FTP／SCM basic credentials 停用等既有安全設定保持不變。
- `capacity: 1`，不啟用自動水平擴充。

### 4.1 SQL Basic 與 Serverless 決策

| 比較項目 | SQL Basic 5 DTU | General Purpose Serverless |
| --- | --- | --- |
| 計費方式 | 固定 DTU 與固定月費 | 使用中依 vCore／秒計費，暫停時只收 storage |
| West US 2 運算費 | 約 US$0.161／日，平均約 US$4.90／月 | Gen5 約 US$0.521758／vCore-hour；最低 0.5 vCore 時約 US$0.260879／online hour |
| 可用性體驗 | 持續 Online，沒有 auto-resume 延遲 | 閒置後可 auto-pause；第一次連線可能收到暫時錯誤並等待 resume |
| 最低設定 | 5 DTU、2 GB、30 concurrent workers／logins | 0.5–2 vCore、auto-pause 預設 60 分鐘 |
| 適合情境 | 固定公開 Demo、希望費用與回應時間可預測 | 每月只有極少數使用時段、可接受冷啟動與 retry |

以目前 Retail Prices 計算，純付費 Serverless 在最低 0.5 vCore 下，每月 Online 超過約 **18.77 小時**，運算費就高於 Basic，且尚未包含 storage。免費 offer 的 100,000 vCore seconds 換算後，最低 0.5 vCore 約可 Online 55.56 小時；但目前免費額度已用完，選擇轉為付費服務後也無法回復原 free offer。

本專案的 public health workflow 每 6 小時執行一次，readiness 會連線 SQL；Azure 也明確說明 open application sessions 會阻止 auto-pause。若每天四次探測各讓 60 分鐘 auto-pause 重新計時，保守估算可形成約 120 online hours／月。此時純付費 Serverless 最低運算費約 US$31.31；即使每月仍先扣 free grant，超額運算費也約 US$16.81。這還沒有計入 storage，且讀者流量會再增加使用時數。

因此書籍公開 Demo 採用 SQL Basic。它的效能上限較低，仍需用 50 concurrent users gate 驗證；但在目前監控頻率、連線方式與新書流量預期下，費用比 Serverless 更可預測，也沒有資料庫 resume 冷啟動。

## 5. 月費模型

### 5.1 估算

| 項目 | West US 2 單價依據 | 月費估算 |
| --- | --- | ---: |
| Static Web Apps Free | US$0 | US$0.00 |
| Linux App Service B1 | Portal／Retail API 約 US$0.017/小時；公開定價頁可能顯示約 US$13.14/月 | US$12.41–13.14 |
| Azure SQL Database Basic | 約 US$0.161/日 | 約 US$4.90 |
| 固定費用合計 | 依當月天數略有差異 | **US$17.31–18.04** |
| 與 US$30 Budget 的差額 | 不含稅、匯率與額外用量 | **US$11.96–12.69** |

### 5.2 不包含項目

- 台幣匯率、信用卡海外手續費與稅。
- 超出免費額度的網路輸出費用。
- 未來新增的 Azure 資源、額外 App Service instance、付費監控或備份選項。
- 部署當天價格變動。

### 5.3 部署成本閘門

實作後的 preflight 必須同時滿足：

1. App Service 僅允許 Linux B1，capacity 必須為 1。
2. Azure SQL 僅允許 Basic 5 DTU，最大 2 GB。
3. Static Web Apps 必須保持 Free。
4. 官方即時零售價格估算不得高於 US$20 固定月費目標。
5. Resource Group Monthly Budget 必須為 NT$960，US$20 Alert Budget 必須為 NT$640；兩者以訂閱帳務幣別 TWD 設定。
6. what-if 不得出現刪除、資源替換、額外 instance 或未核准付費服務。

任一條件不成立就停止部署。

## 6. Budget、告警與最高預算保護

### 6.1 預算設定

| 通知 | 門檻 | 對應金額 | 用途 |
| --- | ---: | ---: | --- |
| Actual 50% | NT$960 Budget 的 50% | NT$480，約 US$15 | 提醒固定月費即將完整入帳 |
| US$20 Alert Budget Actual 100% | NT$640 Budget 的 100% | NT$640，約 US$20 | 固定月費目標已用滿，開始檢查額外用量 |
| Actual 80% | NT$960 Budget 的 80% | NT$768，約 US$24 | 警告已接近最高預算，開始人工處置 |
| Forecasted 100% | NT$960 Budget 的 100% | NT$960，約 US$30 預測 | 在實際超額前預警 |
| Actual 100% | NT$960 Budget 的 100% | NT$960，約 US$30 | 重大費用警示 |

> 2026-08-28 修正：Azure 讀回顯示本訂閱 Budget 單位為 TWD。原本的 `amount: 20` 與 `amount: 30` 實際代表 NT$20 與 NT$30，已改用保守的 NT$640 與 NT$960。US$20／US$30 是政策目標，匯率變動時應重新檢查 TWD 門檻。

Budget 與 Action Group 都應以 Bicep 建立。通知接收者使用 Azure Subscription Owner role；若之後要增加指定 Email，Email 應放在私有部署參數，不寫入公開 repository。

### 6.2 Azure 無法提供的硬限制

Azure Pay-As-You-Go 不支援自訂 US$30 spending limit。Budget 只追蹤與通知，資源不會因 Budget 超額自動停止，且成本資料存在延遲。

因此「最高 US$30」在本計畫中的定義是：

- IaC 與測試禁止更高 SKU、額外 instance 與未核准付費服務。
- 月費正常模型低於 US$20，保留至少約 US$11.96 緩衝。
- US$20 先發目標費用告警、US$24 發高額警告，US$30 發重大警示。
- 超額處理由人確認後執行，不自動刪除資料。

### 6.3 自動降級選項

Azure Budget 可透過 Action Group 觸發 Automation Runbook，但不建議在第一階段啟用：

- `Stop Web App` 不會停止 B1 App Service Plan 計費。
- 真正降低 API 費用必須把 B1 自動降回 F1；這會重新引入 CPU quota，Demo 可能立即無法使用。
- SQL Basic 無法暫停，仍會持續產生約 US$4.90/月費用。
- Cost Management 延遲使自動動作無法精準停在 US$30。

若日後確認「超支時允許 Demo 中斷」，第二階段可在 Actual 80%，即 US$24，觸發 Runbook 將 App Service Plan 降回 F1，保留約 US$6 緩衝。此功能必須另行審核權限、可用性風險與復原步驟。

## 7. 已修改的 IaC、驗證工具與文件

此節是 2026-08-26 的基準實作紀錄；後續 Container Apps Phase 1 變更統一維護在 `ops/azure-book-launch-budget` branch，實際部署狀態以本文開頭與 Azure 回讀結果為準。

| 檔案 | 已完成變更 |
| --- | --- |
| `infra/main.bicep` | 將 `costPolicy` 改為書籍上市預算政策；加入 US$30 與 US$20 Alert Budgets 模組輸出 |
| `infra/modules/app-service.bicep` | F1/Free 改為 B1/Basic、capacity 1、Always On 與 liveness health check |
| `infra/modules/sql-free-database.bicep` | 改名或重構為一般 SQL module；改用 Basic 5 DTU、2 GB，移除 free-limit/serverless 欄位 |
| `infra/modules/cost-guard.bicep` | 新增 Action Group、Monthly NT$960 Budget 與原四組通知；另加 Monthly NT$640 Alert Budget 的 Actual 100% 通知，金額單位明確標示為 TWD |
| `scripts/azure/check_free_skus.py` | 改為付費預算 preflight；查核 B1、SQL Basic、即時價格與 US$20／US$30 閘門 |
| `scripts/azure/preflight.sh` | 呼叫新的預算 preflight |
| `scripts/azure/deploy.sh` | 更新確認訊息與付費方案輸出；仍保留 what-if 與人工確認 |
| `tests/test_azure_preflight.py` | 驗證價格估算、固定月費與 Budget 上限 |
| `tests/test_infra_guardrails.py` | 驗證 B1、capacity 1、SQL Basic 5 DTU、2 GB 與 Budget 通知 |
| `tests/test_deployment_contract.py` | 驗證付費 preflight 必須在 what-if／create 之前執行 |
| `scripts/load_test.py` | 新增 read-mostly 20／50／100 concurrent users 上市容量驗收工具；密碼與 token 不寫入輸出 |
| `tests/test_load_test.py` | 驗證 error rate、GET p95 與 health gate 判定 |
| 既有 deployment／operations 文件 | 實作通過後，將 Free 現況更新為已核准的書籍上市方案；不改寫既有 tags/releases |

## 8. 實作與部署階段

### Phase 0：計畫核准

完成條件：

- 確認 B1 + SQL Basic 方案。
- 確認正常月費目標 US$15–20。
- 確認 US$30 是 Budget／告警與部署規格上限，不是 Azure 硬停損。
- 確認第一階段不啟用自動降級。
- 確認 SQL 從 Free offer 轉為付費層後無法回復原免費優惠。

### Phase 1：IaC 與測試

1. 從乾淨 `main` 建立獨立 `ops/azure-book-launch-budget` branch。
2. 先修改 guardrail tests，確認測試會因現行 Free 設定失敗。
3. 修改 Bicep、preflight、deploy script 與必要文件。
4. 不修改 application business code、資料庫 schema 或讀者資料。

完成閘門：

- `pytest`、Ruff 與離線 final verifier 通過。
- Bicep build 通過。
- Git diff 只包含核准的部署、測試與文件。
- 無 credential、token、連接字串或個人 Email 進入 Git。

### Phase 2：Azure 唯讀預檢

1. 使用正確 tenant 與 subscription 登入 Azure CLI。
2. 確認目標只有 `hlr-eric861129-v2-rg`。
3. 讀取現行 App Service、SQL Database、Budget 與 Action Group 設定。
4. 用官方 Retail Prices API 重新計算 West US 2 月費。
5. 執行 Bicep what-if。

what-if 只允許：

- 新增 1 個 Action Group。
- 新增 1 個 Resource Group Budget。
- App Service Plan F1 修改為 B1，capacity 保持 1。
- Azure SQL Database Free General Purpose Serverless 修改為 Basic 5 DTU。
- App Service 的 Always On／health check 設定修改。

任何 delete、replace、區域變更、新增 instance、SQL Server 重建或其他付費資源都必須停止。

### Phase 3：付費變更

套用前再次顯示實際月費與 what-if 摘要，取得當下確認後才執行：

1. 先建立 US$30 Budget、US$20 Alert Budget 與 Action Group。
2. 將 Azure SQL 改為 Basic 5 DTU並等待 Online。
3. 將 App Service Plan 改為 B1、capacity 1。
4. 套用 Always On 與 `/health/live` health check。
5. 不調整 Static Web Apps Free。

預期服務影響：SQL service tier 切換時，既有連線可能短暫中斷；Microsoft 說明通常少於 30 秒，但應以實際結果為準。API 必須具備連線重試並在切換後重新驗證 readiness。

### Phase 4：部署後驗證

依序驗證：

1. Azure 實際 SKU 與 instance count。
2. US$30 Budget、US$20 Alert Budget、合計五組通知與 Action Group 狀態。
3. 前端、API root、`/health/live`、`/health/ready`、`/docs` 全部 HTTP 200。
4. 註冊、登入、Habit CRUD、check-in、重複 check-in 409、獎勵與 archive 的 reader journey。
5. Azure SQL 狀態 Online，資料量與主要資料筆數未漂移。
6. GitHub backend／frontend workflow 與 public health workflow 狀態。

2026-08-26 實際結果：

- Azure subscription deployment `hlr-book-v2-westus2` 為 `Succeeded`。
- App Service Plan 是 `B1/Basic`、capacity 1；`Always On=true`，health check path 為 `/health/live`。
- Azure SQL 是 `Basic` 5 DTU、2 GB、`Online`；原 free-limit、serverless 與 auto-pause 欄位均已移除。
- Static Web Apps 維持 `Free`。
- `hlr-eric861129-v2-monthly-budget` 為 Monthly NT$960，Actual 50／80／100% 與 Forecasted 100% 四組通知皆啟用；`hlr-eric861129-v2-usd20-alert-budget` 為 Monthly NT$640，Actual 100% 通知啟用。兩個 Budget 都連到 Subscription Owner Action Group，約對應 US$30 與 US$20 政策目標。
- 前端、API root、`/health/live`、`/health/ready` 與 `/docs` 全部 HTTP 200。
- Reader journey 的 register、login、Habit create/list、check-in、重複 check-in 409、profile reward 與 archive 全部通過。
- SQL `storage` 指標為 23,658,496 bytes，allocated data storage 為 33,554,432 bytes，與部署前文件記錄的約 22 MB 同量級。因部署前沒有主要資料表筆數快照，且本機 IP 不在 SQL firewall allowlist，未為驗證而擴大 firewall；因此「主要筆數未漂移」無法用前後快照證明。
- 手動觸發的唯讀 GitHub public-health run `32943929658` 成功；最近 backend 與 frontend deployment workflows 均為 success。本次 SKU 變更沒有重新部署 application artifact。

## 9. 新書流量驗收

B1 + SQL Basic 是最低固定付費層，不直接等同上市容量。正式宣告可供讀者使用前，執行 read-mostly 負載測試：

| 階段 | 流量 | 時間 | 用途 |
| --- | ---: | ---: | --- |
| 基準 | 20 concurrent users | 10 分鐘 | 一般讀者流量 |
| 上市門檻 | 50 concurrent users | 5 分鐘 | 短時間集中使用 |
| Burst | 100 concurrent users | 1 分鐘 | 連結公開後瞬間流量 |

負載測試只大量執行 login、Habit list、profile 等讀取路徑；寫入流程只跑單次 reader journey，避免大量建立無法自動清除的帳號與資料。

上市通過條件：

- 20 與 50 concurrent users 階段的 HTTP error rate 小於 1%。
- 主要 GET API p95 小於 2.5 秒。
- `/health/live` 與 `/health/ready` 持續 HTTP 200。
- App Service CPU 平均低於 75%、記憶體低於 80%。
- Azure SQL DTU 使用率不持續超過 80%，Failed Connections 沒有持續增加。
- 100-user burst 結束後 2 分鐘內恢復正常，沒有持續性 5xx。

若 50-user 階段未通過，不得宣稱目前方案足以承受新書流量。後續需重新評估提高 SQL／App Service 預算，或改採可 scale-to-zero 的 Container Apps 架構。

### 9.1 2026-08-26 實測結果：未通過，已停止升階

正式 workload 使用 1 秒 think time；每位 virtual user 在階段開始時登入一次，之後重複 Habit list 與 profile GET。這符合一般讀者取得 token 後持續操作的 read-mostly 行為。

| 階段 | Request 結果 | GET p95 | Health | Azure 資源 | 判定 |
| --- | --- | ---: | --- | --- | --- |
| 20 users／10 分鐘 | 7,874 requests；5 次連線層錯誤；error rate 0.064% | 0.727 秒 | 0 failure | App CPU 平均 31.1%、峰值 61%；Memory 平均 58.7%、峰值 65%；SQL CPU 峰值 14%、failed connections 0 | 通過 |
| 50 users／5 分鐘 | 3,272 requests；50 次連線層錯誤；error rate 1.528% | 0.889 秒 | 1 failure | App CPU 平均 45.8%、峰值 86%；Memory 平均 65%、峰值 95%；SQL CPU 峰值 14%、failed connections 0 | 未通過 |
| 100 users／1 分鐘 | 50-user gate 失敗後立即停止，未形成有效 burst 結果 | 未測 | 未測 | 未測 | 不執行 |

Azure App Service 在 50-user 時間窗記錄 3,384 requests、0 次 5xx；本機工具的 50 次 status 0 代表連線或 timeout 未取得 HTTP response，而不是伺服器回傳 5xx。停止後曾有 root／ready request timeout，隨後在 2 分鐘內恢復，root、live、ready 連續兩輪 HTTP 200。

另做過一次診斷性「每輪都重新 login」壓力測試；該情境在 20 users 就讓 App CPU 平均 89.5%、Memory 平均 80.88%，因此不應把高頻密碼驗證與一般 read-mostly 流量混為一談，但它證明大量同時登入仍是 B1 的明確風險。

結論：B1 可通過 20 concurrent users 的一般讀取基準，但 50-user 上市門檻未通過，因此目前仍不得宣稱已承受新書上市流量。SQL Basic 並非瓶頸；下一步應優先分析登入密碼雜湊成本、App Service worker/process 設定與 timeout，再決定是否優化後重測或提高 App Service SKU。在 US$30 Budget 下直接升到更高固定 SKU 會大幅壓縮成本緩衝，必須另案估價與核准。

## 10. 回復與事故處理

### 10.1 App Service

- 可將 B1 降回 F1 以停止 B1 固定費用。
- 降回 F1 後會重新受到每日 CPU quota 限制，應視為停用或降級服務，不是健康回復。
- 不刪除 Web App、Plan 或部署紀錄。

### 10.2 Azure SQL

- Free offer 轉為付費 service tier 後，無法回復原免費優惠。
- SQL Basic 無法暫停；停止 API 不會停止 SQL Basic 計費。
- 若 API 必須停用，資料庫先保留 Basic，等人工決定是否遷移到 paid serverless；禁止自動刪除資料庫。
- Service tier 切換本身不應遺失資料，但切換前後都要核對狀態、資料量與 readiness。

### 10.3 IaC

- 未部署前可直接放棄 ops branch，不影響 Azure。
- 部署後只能回復可逆設定；不得用舊 Free Bicep 覆寫造成未預期轉換。
- 已出版 chapter branches、tags、releases 保持不變。

## 11. 風險清單

| 風險 | 影響 | 控制方式 |
| --- | --- | --- |
| Budget 不是硬上限 | 帳單可能超過 US$30 | 固定 SKU、單一 instance、NT$640／NT$768 預警、NT$960 告警、部署 preflight |
| 成本資料延遲 8–24 小時 | 告警不是即時 | 保留至少約 US$11.96 緩衝，不依賴超額後自動停機 |
| SQL Basic 效能有限 | 新書流量可能造成延遲或 5xx | 50-user gate 與 100-user burst test |
| SQL 付費轉換不可回復 Free offer | 產生持續約 US$4.90 月費 | 執行前再次確認；禁止自動刪除 |
| B1 只有單一 instance | API 沒有水平容錯 | health check、Always On、事故 runbook、負載測試 |
| Portal 手動修改造成 IaC drift | 後續部署可能覆寫設定 | 只透過經 what-if 的 Bicep／Azure CLI 套用 |
| 公開流量造成異常資料 | Demo 資料品質下降 | 保留現有隱私聲明；負載測試採 read-mostly |

## 12. 使用者確認清單

請在進入實作前確認：

- [x] 同意 App Service 使用 Linux B1、capacity 1。
- [x] 同意 Azure SQL 使用 Basic 5 DTU、2 GB。
- [x] 同意正常固定月費目標為 US$15–20。
- [x] 同意 Resource Group Monthly Budget 為 US$30。
- [x] 理解 Budget 不會自動停止服務，也無法保證帳單精準停在 US$30。
- [x] 同意第一階段只告警，不建立自動降級或自動刪除。
- [x] 理解 SQL 轉為付費 service tier 後無法回復原 Free offer。
- [x] 同意 50 concurrent users 負載測試是新書公開前的最低上市門檻。
- [x] 同意實作只修改目前 main 的新 ops branch，不重寫已出版 branches、tags、releases。

確認文字：`確認此規劃，可以進入 IaC 實作與 what-if 階段；Azure 實際付費變更前再確認一次。`

## 13. 參考資料

- [Azure App Service quotas and quota enforcement](https://learn.microsoft.com/en-us/azure/app-service/web-sites-monitor)
- [App Service for Linux pricing](https://azure.microsoft.com/en-us/pricing/details/app-service/linux/)
- [Manage an App Service plan](https://learn.microsoft.com/en-us/azure/app-service/app-service-plan-manage)
- [Azure SQL Database free offer FAQ](https://learn.microsoft.com/en-us/azure/azure-sql/database/free-offer-faq?view=azuresql)
- [Azure SQL DTU purchasing model](https://learn.microsoft.com/en-us/azure/azure-sql/database/service-tiers-dtu?view=azuresql)
- [Azure SQL DTU single-database limits](https://learn.microsoft.com/en-us/azure/azure-sql/database/resource-limits-dtu-single-databases?view=azuresql)
- [Azure SQL Serverless overview](https://learn.microsoft.com/en-us/azure/azure-sql/database/serverless-tier-overview?view=azuresql)
- [Azure SQL Serverless FAQ](https://learn.microsoft.com/en-us/azure/azure-sql/database/serverless-tier-faq?view=azuresql)
- [Scale Azure SQL Database resources](https://learn.microsoft.com/en-us/azure/azure-sql/database/single-database-scale?view=azuresql)
- [Create and manage Azure budgets](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets)
- [Azure spending limit](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/spending-limit)
- [Azure Retail Prices REST API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices)
- [Microsoft.Consumption/budgets Bicep reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.consumption/2024-08-01/budgets)
