# HLR 監控規範

## 監控目標

HLR 是 Container Apps Consumption 與 SQL Basic 的公開書籍 Demo；B1 只在遷移後至少 48 小時作為 rollback。監控目標是辨識 cold start、持續故障、容量不足、資料庫不可用，以及費用達 NT$640 告警或接近 NT$960 Budget。這兩個 TWD 金額分別約為 US$20 與 US$30。

## 主動探測

`.github/workflows/public-health.yml` 每 6 小時執行一次，也可由 GitHub Actions 手動觸發。它以 `--read-only` 驗證前端、API 根網址、liveness、readiness 與 Swagger UI，失敗時由 GitHub Actions 的失敗通知負責告警。排程不建立任何讀者資料。

本機或事故處理時可執行：

```bash
python scripts/smoke_test.py \
  --urls docs/deployment/public-urls.json \
  --read-only
```

## Azure Monitor 內建指標

不連接 Log Analytics workspace。值班者直接在 Azure Portal 的 Metrics 頁面查看下列平台指標：

| 資源 | 指標 | 調查門檻 | 第一個動作 |
| --- | --- | --- | --- |
| Container Apps | HTTP 5xx | 暖機後 15 分鐘內連續出現 | 檢查 active revision、replica restart、`/health/live` 與即時 console stream |
| Container Apps | Response Time | scale-from-zero 後持續高於 5 秒 | 檢查 replica 數、HTTP concurrency 與 SQL readiness |
| Container Apps | Replica Count | 長時間維持 2，或頻繁 restart | 檢查流量、memory 與 OOM；不自動提高上限 |
| App Service B1 rollback | CPU／Memory | 48 小時觀察期異常 | 只用於回復，不把它當長期容量來源 |
| Azure SQL | Failed Connections | 15 分鐘內持續增加 | 檢查 App Settings、firewall 與資料庫狀態 |
| Azure SQL | Data space used percent | 高於 80% | 清理教學測試資料，不提高付費容量 |
| Azure SQL Basic | DTU Percentage | 持續高於 80% | 找出高成本查詢並評估上市容量 |
| Resource Group NT$640 Alert Budget | Actual 100% | 達 NT$640，約 US$20 | 檢查是否有固定月費外的額外用量 |
| Resource Group NT$960 Budget | Actual 80% | 達 NT$768，約 US$24 | 人工檢查本月成本與新增資源 |
| Resource Group NT$960 Budget | Actual／Forecasted 100% | 達到或預測 NT$960，約 US$30 | 重大費用警示，人工決定是否降級 API |
| Static Web Apps | Requests／Bandwidth | 異常突增 | 檢查公開流量與 GitHub 部署紀錄 |

## 狀態分級

- `正常`：五個公開網址皆為 200。
- `觀察`：scale-to-zero 後第一次探測失敗，但 2 分鐘內重試成功；記錄為 cold start。
- `事故`：暖機後仍失敗、readiness 連續 503，或前端無法載入 production bundle。
- `容量警示`：B1 CPU／記憶體或 SQL DTU 持續超過門檻；先記錄量測結果，不自動提高 SKU。
- `費用警示`：Actual 達 NT$640、達 NT$768，或 Actual／Forecasted 達 NT$960；Budget 只通知，不會自動停止服務。

每次事故至少記錄 UTC 時間、受影響網址、HTTP 狀態、部署 commit、Azure 資源狀態、處置與恢復時間。不得把密碼、JWT、deployment token 或完整 App Settings 放入紀錄。
