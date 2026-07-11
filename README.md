# Habit Life RPG

《左手藍圖，右手魔法》的累進式隨書範例專案。讀者可以切換公開章節分支，看到產品如何從安全的開發現場，逐步成長為部署在 Azure 的完整 MVP。

## 目前章節

| 章節 | 分支 | 本階段成果 |
| --- | --- | --- |
| 第 2 章：工具箱 | `chapter/02-toolbox` | 安全環境範本、Git 規範、AI 協作規則與可驗證開發現場 |
| 第 3 章：藍圖繪製 | `chapter/03-blueprint` | PRD、User Stories、UX Flow、UI Spec 與完整 MVP 邊界 |
| 第 4 章：系統架構 | `chapter/04-architecture` | SQLAlchemy 模型、Alembic migration 與 OpenAPI 契約 |
| 第 5 章：後端開發 | `chapter/05-backend` | FastAPI、JWT、Habit CRUD、每日打卡、Streak 與獎勵交易 |
| 第 6 章：品質保證 | `chapter/06-quality` | Pytest、Ruff、OpenAPI parity 與 GitHub Actions 品質閘門 |
| 第 7 章：前端開發 | `chapter/07-frontend` | React 響應式界面、帳號流程、Habit 管理與每日打卡 |

後續章節會在前一個分支之上累進，不會要求讀者自行合併零散程式碼。

## 第 2 章開始方式

```bash
git clone https://github.com/eric861129/Habit-Life-RPG.git
cd Habit-Life-RPG
git switch chapter/02-toolbox
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

將 `.env` 的 `HLR_JWT_SECRET` 換成自己的長隨機字串，再執行：

```bash
python scripts/verify_environment.py
python -m pytest -q
```

`.env.example` 只提供可公開的變數名稱與假值；`.env` 永遠不進 Git。

## 第 5 章後端啟動

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
alembic upgrade head
python -m backend.app.seed
python -m uvicorn backend.app.main:app --reload --port 8000
```

執行 seed 前必須先替換 `.env` 的 `HLR_DEMO_PASSWORD`。API 文件位於 `http://localhost:8000/docs`；應用程式不會在每次啟動時自動重建或重設示範資料。

## 第 7 章完整 MVP

先依上一節啟動 API，再開另一個終端啟動 React：

```bash
cd frontend
cp .env.example .env
npm ci
npm run dev
```

前端預設位於 `http://localhost:5173`。本機開發時 API 主機會跟隨瀏覽器使用的 hostname；Azure 或其他環境則在建置時透過 `VITE_API_BASE_URL` 指定 HTTPS API 網址。

可以另行執行前端品質閘門：

```bash
npm test -- --run
npm run build
```

## 版本策略

- `archive/pre-rebuild-20260711`：重建前的完整舊版。
- `chapter/02-toolbox` 到 `chapter/10-agent-ready`：可直接執行的累進章節狀態。
- `book-v2-chXX-*`：與章節分支對應的不可變 Tag 與 GitHub Release。
- `main`：全書最終、已驗證且已部署的版本。

## 安全原則

不要提交密碼、JWT Secret、Azure 連線字串、部署 Token、Publish Profile 或付款資訊。任何不確定能否公開的值，先留在本機 `.env`，只將變數名稱寫入 `.env.example`。
