# HLR Agent 工作流程

## Context

Agent 先讀 `AGENTS.md`、PRD、系統架構、資料庫與 OpenAPI 契約，再讀目前章節指南。不要一次把整個 Repository 塞進提示；只載入與任務直接相關的檔案與測試。

## Plan

先寫出可驗收的最小變更與風險：產品邊界、SQLite／Azure SQL 差異、前後端契約、讀者連結與 Azure 零費用限制。涉及行為變更時，先定義會失敗的測試。

## Implement

維持章節累進，不改寫已發布 Tag。安全、資料庫與部署問題必須修正根因，不得關閉驗證、放寬 CORS、移除 constraint 或改成付費 SKU 來讓流程通過。

## Verify

完整驗證入口：

```bash
python scripts/final_verify.py
```

離線或 pre-push 驗證：

```bash
python scripts/final_verify.py --skip-live
```

可選擇為目前 clone 啟用 Hook：

```bash
bash scripts/install_hooks.sh
```

Hook 只執行離線驗證，不會碰 Azure 或建立讀者資料。正式網址探測使用唯讀 GET；完整 reader journey 只在部署驗收時明確執行。

## Handoff

交接內容必須包含變更 commit、測試結果、公開網址、Azure 實際 SKU、資料 migration 狀態、已知免費層限制與回復版本。不得附上密碼、JWT、OIDC token、SWA deployment token 或 App Settings 值。

Repository 內的 `.codex/skills/hlr-release/SKILL.md` 將上述發版規則整理成可重用 Skill；`AGENTS.md` 是所有 Agent 的專案邊界與禁止事項。
