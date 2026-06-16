# Habit Life RPG

《左手藍圖，右手魔法：用文件驅動 AI 開發》的隨書範例專案。

這個 repository 不是一次放上最終成品，而是會依照書中的章節逐步長出來。讀者可以透過 Git tag 或 GitHub Releases，切回每一章完成時的狀態，跟著書本從工具箱、藍圖、後端、測試、前端一路走到部署與維運。

## 目前進度

| 階段 | Tag | 狀態 | 內容 |
| :--- | :--- | :--- | :--- |
| 第 2 章：工具箱 | `ch02-toolbox` | 已完成 | Repo 基礎、資安規則、章節導覽、圖片資產清單 |
| 第 3 章：藍圖繪製 | `ch03-blueprint` | 已完成 | PRD、User Stories、UX Flow、復古像素 RPG UI Spec、靜態原型 |
| 第 4 章：地基工程 | `ch04-architecture` | 已完成 | 系統架構圖、資料庫綱要、OpenAPI 契約 |
| 第 5 章：後端開發 | `ch05-backend-sqlite` | 已完成 | FastAPI + SQLite 本機後端、habit check-in API |
| 第 6 章：品質保證 | `ch06-quality-pytest` | 已完成 | Pytest、本機隔離測試資料庫、API 測試矩陣 |
| 第 7 章：前端開發 | `ch07-frontend-local` | 已完成 | React + Vite + TypeScript + Tailwind 本機前端整合 |
| 第 8 章：雲端部署 | `ch08-cloud-templates` | 尚未開始 | Azure SQL / App Service / SWA 範本與部署文件 |
| 第 9 章：維運合規 | `ch09-ops` | 尚未開始 | Runbook、監控、告警、隱私權政策 |
| 第 10 章：Agent 視野 | `ch10-agent-ready` | 尚未開始 | Agent 工作流與下一個專案 checklist |

## 讀者如何使用

查看所有章節標籤：

```bash
git tag --list
```

切到某個章節完成時的狀態：

```bash
git checkout ch02-toolbox
git checkout ch03-blueprint
git checkout ch04-architecture
git checkout ch05-backend-sqlite
git checkout ch06-quality-pytest
git checkout ch07-frontend-local
```

回到最新進度：

```bash
git checkout main
git pull
```

## 第 7 章前端開發

第 7 章把第 3 章復古像素 RPG 靜態原型重建成 React + Vite + TypeScript + Tailwind 前端，並串接第 5 章 FastAPI API。

本章交付物：

- `frontend/`
- `frontend/src/api/client.ts`
- `frontend/src/components/`
- `frontend/src/styles/index.css`
- `tests/test_cors.py`
- `docs/chapter-guides/ch07-frontend-local.md`
- `docs/book-assets/ch07-frontend/`

小節 checkpoint：

```bash
git checkout ch07-1-vite-foundation
git checkout ch07-2-rpg-ui-shell
git checkout ch07-3-api-integration
git checkout ch07-4-interaction-states
git checkout ch07-5-visual-qa-assets
git checkout ch07-frontend-local
```

本章啟動方式：

```bash
python -m uvicorn backend.app.main:app --reload --port 8000
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

若 macOS 環境沒有 `python` 指令，可改用：

```bash
python3 -m uvicorn backend.app.main:app --reload --port 8000
```

前端預設讀取：

```text
VITE_API_BASE_URL=http://localhost:8000
VITE_DEV_AUTH_TOKEN=local-dev-token
```

第七章不提供 mock fallback。讀者必須先啟動後端，再啟動前端，才能看到真實 API 回傳的 Hero Status、Quest Log、打卡成功與錯誤狀態。

## 第 6 章品質保證

第 6 章不新增產品功能，而是把第 5 章後端行為變成可重複執行的 Pytest 防線。

本章交付物：

- `tests/conftest.py`
- `tests/test_ch05_smoke.py`
- `tests/test_user_api.py`
- `tests/test_habits_api.py`
- `tests/test_rewards.py`
- `docs/chapter-guides/ch06-quality-pytest.md`
- `docs/book-assets/ch06-quality/`

小節 checkpoint：

```bash
git checkout ch06-1-test-fixtures
git checkout ch06-2-api-contract-tests
git checkout ch06-3-reward-tests
git checkout ch06-4-docs-quality
```

本章測試方式：

```bash
python -m pytest -q
```

第六章採用每個測試獨立 SQLite 暫存檔，並用 FastAPI dependency override 避免污染本機 `habit_life_rpg.db`。

第六章只做本機 Pytest，不建立 GitHub Actions CI、不建立 React app、不碰 Azure、不做正式登入註冊或 Alembic migration。

## 第 5 章後端開發

第 5 章依照第 4 章契約建立本機 FastAPI + SQLite 後端，讓 `Habit Life RPG` 的核心 API 可以實際執行。

本章交付物：

- `pyproject.toml`
- `backend/app/main.py`
- `backend/app/database.py`
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/security.py`
- `backend/app/routers/user.py`
- `backend/app/routers/habits.py`
- `backend/app/services/rewards.py`
- `tests/test_ch05_smoke.py`
- `docs/chapter-guides/ch05-backend-sqlite.md`
- `docs/book-assets/ch05-backend/`

小節 checkpoint：

```bash
git checkout ch05-1-fastapi-skeleton
git checkout ch05-2-sqlite-models
git checkout ch05-3-profile-habits-api
git checkout ch05-4-checkin-api
```

本章啟動方式：

```bash
python -m pip install -e ".[dev]"
python -m uvicorn backend.app.main:app --reload --port 8000
```

本章使用 development-only token：

```http
Authorization: Bearer local-dev-token
```

第五章仍不包含 React app、Azure 部署、Alembic migration、正式登入註冊流程或完整 Pytest 測試矩陣。這些會在後續章節依序展開。

## 第 4 章地基工程

第 4 章把產品藍圖翻成工程契約，不提前建立 FastAPI、SQLite database、React app 或 Azure 資源。

本章交付物：

- `docs/system-architecture.md`
- `docs/database-schema.md`
- `docs/openapi.yaml`
- `docs/api-contract.md`
- `docs/chapter-guides/ch04-architecture.md`
- `docs/book-assets/ch04-foundation/`

小節 checkpoint：

```bash
git checkout ch04-1-system-architecture
git checkout ch04-2-database-schema
git checkout ch04-3-openapi-contract
```

第四章正式鎖定 API 契約：`POST /api/v1/habits/{habit_id}/checkin` 成功時回傳 `current_exp`、`current_gold`、`current_level` 與 `leveled_up`，後續後端、測試與前端都必須對齊這份契約。

## 第 3 章藍圖文件

第 3 章把產品從想法整理成可施工文件，不提前寫正式後端或 React 前端。

本章交付物：

- `docs/PRD.md`
- `docs/user-stories.md`
- `docs/ux-flow.md`
- `docs/ui-spec.md`
- `prototype/static/index.html`
- `docs/chapter-guides/ch03-blueprint.md`
- `docs/book-assets/ch03-blueprint/`

小節 checkpoint：

```bash
git checkout ch03-1-prd
git checkout ch03-2-user-stories
git checkout ch03-3-ux-flow
git checkout ch03-4-ui-spec-static
```

`prototype/static/index.html` 是第 3 章的復古像素 RPG 風格靜態原型。它只展示遊戲化 UI：Hero Status、任務捲軸式 Quest Log、Reward 與底部導覽，不使用遊戲引擎，也不接 API。

## 第 2 章起手式

第 2 章只建立安全的開發現場，不提前寫後端或前端功能。

你應該先確認：

- `.gitignore` 已排除 `.env`、虛擬環境、`node_modules` 與建置產物。
- `.env.example` 只放變數名稱與假值，不放任何真實秘密。
- `AGENTS.md` 已記錄本專案的 AI 協作規則。
- `docs/chapter-guides/ch02-toolbox.md` 說明本章完成條件。
- `docs/book-assets/assets-register.md` 追蹤書中圖片素材。

## 主線契約

- 專案名稱：`Habit Life RPG`
- 書中 DDD：Document-Driven Development，不是 Domain-Driven Design
- 核心 API：`POST /api/v1/habits/{habit_id}/checkin`
- 系統命名：進入資料表、API、測試與程式碼後，一律使用 `habit` / `habits` / `habit_id`
- MVP 資料模型：`Users` 與 `Habits`
- 同日不可重複打卡：MVP 先以 `Habits.LastCheckIn` 示範

## 安全提醒

不要把真實密碼、API Key、JWT secret、Azure 連線字串或任何付款資訊提交到 repository。

如果不確定某個值能不能提交，請先放進 `.env`，並只把變數名稱同步到 `.env.example`。
