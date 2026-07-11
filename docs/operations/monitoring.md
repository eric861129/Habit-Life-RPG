# HLR 監控規範

## 監控目標

HLR 是無 SLA 的公開教學展示環境。監控目標是辨識持續故障、免費配額耗盡與資料庫不可用，不把正常的 F1／serverless 冷啟動誤判為重大事故。

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
| App Service | HTTP 5xx | 15 分鐘內連續出現 | 檢查 `/health/live` 與 container log |
| App Service | Average Response Time | 暖機後持續高於 5 秒 | 檢查 CPU Time 與 SQL readiness |
| App Service F1 | CPU Time | 接近每日免費配額 | 降低探測頻率並等待配額重置 |
| Azure SQL | Failed Connections | 15 分鐘內持續增加 | 檢查 App Settings、firewall 與資料庫狀態 |
| Azure SQL | Data space used percent | 高於 80% | 清理教學測試資料，不提高付費容量 |
| Azure SQL free offer | Free amount remaining | 接近 0 | 接受 `AutoPause`，等待下月重置 |
| Static Web Apps | Requests／Bandwidth | 異常突增 | 檢查公開流量與 GitHub 部署紀錄 |

## 狀態分級

- `正常`：五個公開網址皆為 200。
- `觀察`：第一次探測失敗，但 2 分鐘內重試成功；記錄為冷啟動。
- `事故`：暖機後仍失敗、readiness 連續 503，或前端無法載入 production bundle。
- `配額停止`：Azure 明確顯示 F1 或 SQL 免費額度耗盡；不得改用付費 SKU，自動等待配額重置並在 README／Issue 說明。

每次事故至少記錄 UTC 時間、受影響網址、HTTP 狀態、部署 commit、Azure 資源狀態、處置與恢復時間。不得把密碼、JWT、deployment token 或完整 App Settings 放入紀錄。
