# 第 5 章：後端開發

`chapter/05-backend` 依照第 4 章資料與 OpenAPI 契約，完成可本機執行的 FastAPI 後端。

## 已完成

- Argon2 密碼雜湊與 JWT 註冊／登入。
- Profile 與 Habit CRUD。
- 使用 `user_id` 保護資料所有權。
- HabitCheckin ledger 與同日唯一約束。
- Streak、`40 EXP`、`8 gold` 與 `level × 200` 升級規則。
- 公開 liveness 與 database readiness。
- 只在明確執行命令時建立的 idempotent Demo seed。

## 執行

```bash
python -m pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
python -m backend.app.seed
python -m uvicorn backend.app.main:app --reload --port 8000
```

請先替換 `.env` 的 JWT Secret 與 Demo password。互動式 API 文件位於 `http://localhost:8000/docs`。

## 驗證

```bash
python -m pytest -q
python -m ruff check backend tests scripts
```

`chapter/06-quality` 會把 OpenAPI parity、CI 與乾淨安裝變成正式品質閘門。
