# 第 9 章：永續經營

`chapter/09-operations` 將已部署的 HLR 交給可重複執行的維運流程，不增加 Azure 付費服務。

## 本章成果

- `docs/operations/runbook.md`：冷啟動、5xx、資料庫與部署事故的處理順序。
- `docs/operations/monitoring.md`：Azure Monitor 內建指標、人工門檻與 GitHub 唯讀探測。
- `docs/operations/privacy-policy.md`：公開示範環境實際蒐集、保存與處理的資料說明。
- `.github/workflows/public-health.yml`：每 6 小時及手動執行的唯讀公開網址驗證。
- `docs/deployment/public-urls.json`：不含祕密、可供 CI 與讀者查閱的正式網址清冊。

## 維運原則

1. 先判斷 F1 或 SQL serverless 冷啟動，再判斷真正事故。
2. 只用內建 Azure Monitor metrics；不建立 Log Analytics workspace 或可能計費的 Alert 規則。
3. GitHub 排程只做 GET，不建立帳號、Habit 或 Check-in。
4. 任何 SKU、SQL free-limit 行為或區域變更前，都重新執行 preflight 與 what-if。
5. 示範環境沒有 SLA，不保存讀者唯一副本，也不應接收敏感資料。
