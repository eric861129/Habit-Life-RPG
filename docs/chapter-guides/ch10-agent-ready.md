# 第 10 章：Agent-ready 最終交付

`chapter/10-agent-ready` 是全書最終 HLR 版本，將開發、驗證、部署、維運與 Agent 交接收斂成同一份可執行契約。

## 本章成果

- `AGENTS.md`：產品邊界、安全規則、Azure 零費用限制與完成定義。
- `.codex/skills/hlr-release/SKILL.md`：章節發版與公開連結驗證 Skill。
- `.githooks/pre-push`：可選的離線品質 Hook。
- `scripts/final_verify.py`：後端、OpenAPI、前端與正式環境的單一驗證入口。
- `docs/agent-workflow.md`：Context、Plan、Implement、Verify、Handoff 流程。
- `docs/final-checklist.md`：第 2～10 章分支、Tag、Release 與正式網址索引。

## 最終門檻

1. 本機 final verifier 全數成功。
2. GitHub quality gate 無錯誤或 runtime deprecation warning。
3. Backend 與 frontend deployment workflow 的 test job 先成功，再部署。
4. 公開前端、API、Docs、live、ready 與唯讀排程探測成功。
5. 第 2～10 章 branch／Tag／Release 都可匿名開啟且 commit 各自正確。
6. `main` 快轉到本章已驗證 commit，不 force-push、不刪除舊歷史。
