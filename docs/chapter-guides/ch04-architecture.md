# 第 4 章：系統架構

`chapter/04-architecture` 累進包含第 2 章工具箱與第 3 章藍圖，並第一次將產品語言轉成可由程式驗證的工程契約。

## 本章成果

- 前後端分離與信任邊界。
- Users、Habits、HabitCheckins 三張資料表。
- SQLite 與 Azure SQL 共用 SQLAlchemy model。
- 可從空資料庫執行的 Alembic migration。
- 包含 Auth、Profile、Habit CRUD、Check-in 與 Health 的 OpenAPI 3.1 契約。

## 驗證

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check backend tests
alembic upgrade head
```

第 4 章不提供可連線 API；`chapter/05-backend` 才依照這些契約實作 FastAPI。
