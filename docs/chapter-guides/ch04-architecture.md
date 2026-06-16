# 第 4 章導覽：地基工程

對應書稿：第 4 章「地基工程」  
Git tag：`ch04-architecture`  
本章定位：把第 3 章的產品藍圖翻成系統架構、資料庫綱要與 API 契約。

## 本章你會看到什麼

第 4 章仍然不寫正式後端程式。這一章的任務，是先把工程地基畫清楚，讓第 5 章可以照文件建立 FastAPI + SQLite 後端。

本章完成後，repo 會多出：

- `docs/system-architecture.md`：前後端分離架構、本機 MVP 架構與終局 Azure 架構。
- `docs/database-schema.md`：`Users` / `Habits` 資料綱要、ERD、索引與密碼資安底線。
- `docs/openapi.yaml`：OpenAPI 3.0.0 API 契約。
- `docs/api-contract.md`：讀者可讀的 API 契約說明。
- `docs/book-assets/ch04-foundation/`：第四章圖資追蹤說明。

## 章節 checkpoint

讀者可以依照書本順序切換到不同小節完成時的狀態：

```bash
git checkout ch04-1-system-architecture
git checkout ch04-2-database-schema
git checkout ch04-3-openapi-contract
git checkout ch04-architecture
```

回到最新進度：

```bash
git checkout main
git pull
```

## 本章主線

### 4.1 System Architecture

`docs/system-architecture.md` 定義前後端分離架構。

請注意兩張圖的差異：

- 本機 MVP 架構：第 5 章先用 FastAPI + SQLite 跑通。
- 終局 Azure 架構：第 8 章才會部署到 Azure Static Web Apps、Azure App Service 與 Azure SQL。

第四章不建立任何 Azure 資源。

### 4.2 Database Schema

`docs/database-schema.md` 定義 MVP 資料地基。

核心資料表：

- `Users`：玩家身分與角色狀態。
- `Habits`：使用者建立的習慣項目。

重要規則：

- 密碼永遠不存明文，只保存 `password_hash`。
- `Users` 包含 `hp`，支援 PRD 中的懲罰機制。
- MVP 使用 `Habits.last_check_in` 支撐同日不可重複打卡。
- 不在第四章新增 `Checkins` 表。

### 4.3 OpenAPI Contract

`docs/openapi.yaml` 是後續前後端與測試共同遵守的 API 契約。

目前定義三個 endpoint：

```http
GET /api/v1/user/profile
GET /api/v1/habits
POST /api/v1/habits/{habit_id}/checkin
```

打卡成功 response 使用第 3 章 User Stories 的欄位：

```json
{
  "habit_id": 1,
  "checked_in": true,
  "current_exp": 160,
  "current_gold": 43,
  "current_level": 2,
  "leveled_up": false
}
```

錯誤 response 統一使用：

```json
{
  "detail": "..."
}
```

## 第四章邊界

本章不做以下工作：

- 不建立 FastAPI 專案。
- 不建立 SQLite `.db` 檔案。
- 不建立 SQLAlchemy ORM class。
- 不建立 Alembic migration。
- 不建立 React app。
- 不建立 Azure 資源。

## 本章完成檢查

- [x] 系統架構文件已建立。
- [x] 本機 MVP 與終局 Azure Mermaid 圖已建立。
- [x] 資料庫綱要與 ERD 已建立。
- [x] OpenAPI 契約已建立。
- [x] API contract 說明文件已建立。
- [x] 第四章圖資追蹤表已更新。
- [x] 已建立章節 checkpoint tags。

## 下一章銜接

第 5 章會開始真正建立本機後端。

下一章要把本章文件翻成：

- FastAPI project structure。
- SQLite 連線設定。
- `Users` / `Habits` ORM model。
- `POST /api/v1/habits/{habit_id}/checkin` route。
- 基礎登入與授權 guard。

第 5 章實作時，請優先對照 `docs/openapi.yaml` 與 `docs/database-schema.md`，不要讓程式碼自己長出另一套契約。
