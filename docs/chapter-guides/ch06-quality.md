# 第 6 章：品質保證

`chapter/06-quality` 將第 5 章的行為變成可在本機與 GitHub Actions 重跑的品質閘門。

## 品質閘門

- `python -m ruff check backend tests scripts`
- `python -m pytest -q`
- `python scripts/verify_openapi.py`
- 第 7 章起增加 `npm test -- --run` 與 `npm run build`

## 覆蓋風險

- 密碼不保存明文，登入失敗不洩漏帳號是否存在。
- 使用者只能讀寫自己的 Habit。
- 重複 Check-in 不會建立第二筆 ledger 或第二次獎勵。
- Streak 中斷與連續日期都有測試。
- Alembic 能從空資料庫建立 schema，且尊重 `DATABASE_URL`。
- Runtime OpenAPI 的 method、path 與 response status 必須和 `docs/openapi.yaml` 一致。

## CI 行為

CI 包含 backend、contract、frontend 三個 job。第 6 章尚未建立 `frontend/package-lock.json`，frontend job 會留下明確 skip 訊息；第 7 章加入前端後，同一個 job 自動變成必要測試。

下一個累進版本是 `chapter/07-frontend`。
