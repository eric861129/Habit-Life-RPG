# 出版圖片與素材追蹤表

本檔追蹤《左手藍圖，右手魔法》放入 `Habit Life RPG` 範例專案時需要產出的截圖、流程圖、架構圖與核對素材。

所有圖片都必須服務一個讀者動作，不只展示漂亮畫面。

## 圖片安全原則

1. 不截 API Key、連線字串、密碼、訂閱 ID、真實信箱、付款資訊。
2. 如果畫面不可避免出現敏感資訊，正式放入 repo 前必須遮蔽。
3. 雲端服務價格、額度、方案名稱可能改版，截圖只輔助定位，不作永久保證。
4. 每張圖都要有操作目標與核對點。

## 狀態說明

- `planned`：已列入書稿需求，尚未製作。
- `drafted`：已有初稿圖或截圖，尚未完成遮蔽與審查。
- `ready`：已遮蔽敏感資訊，可用於出版流程。
- `deferred`：本 repo 只保留圖說，實際圖檔另交出版社。

## 第 2 章素材

| 圖號 | 圖名 | 類型 | 檔案位置 | 狀態 | 操作目標 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 圖 2-1-1 | VS Code 開發基地畫面 | 截圖 | `docs/book-assets/ch02-toolbox/` | planned | 確認 Explorer、Editor、Terminal 都可使用 |
| 圖 2-1-2 | Codex App 登入與專案授權 | 截圖 | `docs/book-assets/ch02-toolbox/` | planned | 確認 Codex App 已登入並開啟本機專案 |
| 圖 2-2-1 | AI 建築團隊四角色分工 | 表格 / 流程圖 | `docs/book-assets/ch02-toolbox/` | planned | 對照 ChatGPT、NotebookLM、Codex App、Codex CLI |
| 圖 2-3-1 | NotebookLM 建立專案筆記本 | 截圖 | `docs/book-assets/ch02-toolbox/` | planned | 建立 `Habit Life RPG` 專案筆記本 |
| 圖 2-3-2 | 上傳 PRD 到 NotebookLM 來源清單 | 截圖 | `docs/book-assets/ch02-toolbox/` | planned | 第 3 章 PRD 完成後補圖 |
| 圖 2-4-1 | 建立 GitHub Repository | 截圖 | `docs/book-assets/ch02-toolbox/` | planned | 建立 repo 並理解 public/private 與 `.gitignore` |
| 圖 2-4-2 | Codex CLI 協助整理 Git Commit | 截圖 | `docs/book-assets/ch02-toolbox/` | planned | 示範先掃描改動，再產生 commit message |
| 圖 2-5-1 | `.env`、`.env.example` 與 `.gitignore` 的安全分工 | 截圖 | `docs/book-assets/ch02-toolbox/` | planned | 區分秘密、範本與版控排除規則 |

## 第 3 章素材

| 圖號 | 圖名 | 類型 | 檔案位置 | 狀態 | 操作目標 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 圖 3-1-1 | 在 ChatGPT 產出第一版 PRD | 截圖 | `docs/book-assets/ch03-blueprint/` | planned | 示範完整 Prompt 如何引導 ChatGPT 先釐清問題，再產出 PRD 初稿 |
| 圖 3-1-2 | 將 PRD 存成專案文件 | 截圖 | `docs/book-assets/ch03-blueprint/` | planned | 確認 `docs/PRD.md` 已成為可版本控制、可被 AI 讀取的專案文件 |
| 圖 3-1-3 | PRD 上傳至 NotebookLM 圖資室 | 截圖 | `docs/book-assets/ch03-blueprint/` | planned | 確認 NotebookLM 來源清單中已出現 `PRD.md` |
| 圖 3-2-1 | ChatGPT 拆解 User Story 與 AC | 截圖 | `docs/book-assets/ch03-blueprint/` | planned | 示範如何把 PRD 中的功能拆成可測試的使用者故事與驗收標準 |
| 圖 3-2-2 | User Stories 同步至 NotebookLM | 截圖 | `docs/book-assets/ch03-blueprint/` | planned | 確認 NotebookLM 來源清單中同時出現 PRD 與 user-stories 文件 |
| 圖 3-3-1 | ChatGPT 產生 Mermaid UX Flow | 截圖 | `docs/book-assets/ch03-blueprint/` | planned | 示範如何請 ChatGPT 把文字流程轉成 Mermaid 程式碼 |
| 圖 3-3-2 | 在 VS Code 預覽 UX Flow | 截圖 | `docs/book-assets/ch03-blueprint/` | planned | 確認 `docs/ux-flow.md` 的 Mermaid 能在 Markdown Preview 中顯示流程圖 |
| 圖 3-4-1 | Habit Life RPG 介面概念圖 | AI 概念圖 / 截圖 | `docs/book-assets/ch03-blueprint/` | planned | 用 UI Spec 轉成可討論的復古像素 RPG 介面方向 |
| 圖 3-4-2 | 第一版復古像素 RPG 靜態切版預覽 | 截圖 | `docs/book-assets/ch03-blueprint/figure-3-4-2-*.png` | drafted | 展示 `prototype/static/index.html` 的 Hero Status、任務捲軸式 Quest Log、Reward 與底部導覽 |

## 第 4 章素材

| 圖號 | 圖名 | 類型 | 檔案位置 | 狀態 | 操作目標 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 圖 4-1-1 | Habit Life RPG 前後端分離終局架構圖 | Mermaid / 架構圖 | `docs/system-architecture.md` | drafted | 讓讀者理解前端、後端、JSON 契約與 Azure SQL 的資料流 |
| 圖 4-2-1 | Users 與 Habits 資料模型 ERD | Mermaid / ERD | `docs/database-schema.md` | drafted | 對照 `Users`、`Habits`、主鍵、外鍵與 `last_check_in` |
| 圖 4-2-2 | 資料庫規格草案產出畫面 | 截圖 | `docs/book-assets/ch04-foundation/` | planned | 示範如何把資料模型條件交給 ChatGPT 整理成資料庫規格 |
| 圖 4-3-1 | 用 Codex App 產出 OpenAPI 契約 | 截圖 | `docs/book-assets/ch04-foundation/` | planned | 確認 `docs/openapi.yaml` 已建立並包含 check-in endpoint |
| 圖 4-3-2 | OpenAPI 契約同步至 NotebookLM | 截圖 | `docs/book-assets/ch04-foundation/` | planned | 確認 `openapi.yaml` 進入圖資室，後續可查詢欄位名稱 |

## 第 5 章素材

| 圖號 | 圖名 | 類型 | 檔案位置 | 狀態 | 操作目標 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 圖 5-1-1 | FastAPI backend 專案結構 | terminal screenshot | `backend/` | planned | 顯示第五章開始建立後端骨架 |
| 圖 5-1-2 | FastAPI Swagger UI | browser screenshot | `http://127.0.0.1:8000/docs` | planned | 展示本機 API 文件 |
| 圖 5-2-1 | SQLAlchemy Users / Habits models | code screenshot | `backend/app/models.py` | planned | 對照第四章資料庫綱要 |
| 圖 5-3-1 | Profile and habits API response | terminal/API client screenshot | local FastAPI | planned | 展示 `GET /api/v1/user/profile` 與 `GET /api/v1/habits` |
| 圖 5-4-1 | Habit check-in success response | terminal/API client screenshot | local FastAPI | planned | 展示 `current_exp`、`current_gold`、`current_level`、`leveled_up` |
| 圖 5-4-2 | Habit check-in error responses | terminal/API client screenshot | local FastAPI | planned | 展示 400、403、404 的 `{ "detail": "..." }` |

## 第 6 章素材

| 圖號 | 圖名 | 類型 | 檔案位置 | 狀態 | 操作目標 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 圖 6-1-1 | TDD red / green / refactor 流程示意 | diagram / slide | `docs/book-assets/ch06-quality/` | planned | 說明先寫測試、看失敗、補實作、再重構的節奏 |
| 圖 6-1-2 | Pytest 隔離式 SQLite fixture | code screenshot | `tests/conftest.py` | planned | 展示暫存 DB、dependency override 與固定時間 |
| 圖 6-2-1 | Check-in API 測試矩陣 | code screenshot | `tests/test_habits_api.py` | planned | 展示 200、400、401、403、404 測試 |
| 圖 6-2-2 | Pytest 全部通過畫面 | terminal screenshot | `python -m pytest -q` | planned | 展示第六章測試防線完成 |
| 圖 6-3-1 | Reward service 升級規則測試 | code screenshot | `tests/test_rewards.py` | planned | 展示 `+40 EXP`、`+8 gold`、升級與 EXP 不歸零 |
| 圖 6-4-1 | 第六章 Git tag / Release | GitHub screenshot | `ch06-quality-pytest` | planned | 確認讀者可切回第六章完成版本 |

## 核對方式

每次新增圖片後，請確認：

- [ ] 圖片檔案名稱包含圖號。
- [ ] 圖片已遮蔽敏感資訊。
- [ ] 本表狀態已更新。
- [ ] 對應章節導覽文件或 README 已能引導讀者找到圖片。
