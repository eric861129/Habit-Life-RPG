# 第 5 章導覽：後端開發

對應書稿：第 5 章「後端開發」  
Git tag：`ch05-backend-sqlite`  
本章定位：依照第 4 章契約建立本機 FastAPI + SQLite 後端。

## 本章你會看到什麼

第 5 章開始真正寫後端程式，但仍然保持本機 MVP 範圍。這一章的目標，是把第 4 章的系統架構、資料庫綱要與 OpenAPI 契約落成可執行 API。

本章完成後，repo 會多出：

- `pyproject.toml`：Python 專案設定與本機依賴。
- `backend/app/main.py`：FastAPI app 入口。
- `backend/app/database.py`：SQLite engine、session dependency 與 foreign key 設定。
- `backend/app/models.py`：SQLAlchemy `User` / `Habit` models。
- `backend/app/security.py`：development-only bearer token guard。
- `backend/app/routers/user.py`：`GET /api/v1/user/profile`。
- `backend/app/routers/habits.py`：habit list 與 check-in API。
- `backend/app/services/rewards.py`：第 5 章固定 RPG reward 規則。
- `tests/test_ch05_smoke.py`：第五章最小 smoke tests。

## 章節 checkpoint

讀者可以依照書本順序切換到不同小節完成時的狀態：

```bash
git checkout ch05-1-fastapi-skeleton
git checkout ch05-2-sqlite-models
git checkout ch05-3-profile-habits-api
git checkout ch05-4-checkin-api
git checkout ch05-backend-sqlite
```

回到最新進度：

```bash
git checkout main
git pull
```

## 啟動方式

安裝本機 dependencies：

```bash
python -m pip install -e ".[dev]"
```

若 macOS 環境沒有 `python` 指令，可改用：

```bash
python3 -m pip install -e ".[dev]"
```

啟動 FastAPI：

```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

Swagger UI：

```text
http://127.0.0.1:8000/docs
```

## 開發用 API Token

本章使用 development-only token：

```http
Authorization: Bearer local-dev-token
```

這不是正式 JWT，也不是 production auth。正式登入、註冊、密碼驗證與 token 發放會在後續章節擴充。

## API 快速驗證

取得目前玩家狀態：

```bash
curl -s http://127.0.0.1:8000/api/v1/user/profile \
  -H "Authorization: Bearer local-dev-token"
```

取得 habit 清單：

```bash
curl -s http://127.0.0.1:8000/api/v1/habits \
  -H "Authorization: Bearer local-dev-token"
```

完成 habit 打卡：

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/habits/1/checkin \
  -H "Authorization: Bearer local-dev-token"
```

成功 response 必須維持第 4 章契約：

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

## 第五章邊界

本章不做以下工作：

- 不建立 React app。
- 不建立 Azure 資源。
- 不建立 Alembic migration。
- 不建立正式登入註冊流程。
- 不建立完整 Pytest 測試矩陣。
- 不建立完整打卡歷史表。

第 6 章會把測試補成完整防線；第 7 章才會把 API 接到復古像素 RPG 前端。

## 本章完成檢查

- [x] FastAPI app scaffold 已建立。
- [x] SQLite connection 已建立。
- [x] SQLAlchemy `User` / `Habit` models 已建立。
- [x] Development-only bearer token guard 已建立。
- [x] `GET /api/v1/user/profile` 已建立。
- [x] `GET /api/v1/habits` 已建立。
- [x] `POST /api/v1/habits/{habit_id}/checkin` 已建立。
- [x] 第五章 smoke tests 已建立。
- [x] 第五章圖資追蹤表已更新。
- [x] 已建立章節 checkpoint tags。

## 下一章銜接

第 6 章會用 Pytest 把第五章 API 鎖成更穩定的品質防線。

下一章要補上的測試包含：

- 成功打卡會更新 `current_exp` 與 `current_gold`。
- 同日重複打卡回傳 `400 Bad Request`。
- 未登入回傳 `401 Unauthorized`。
- 非本人 habit 回傳 `403 Forbidden`。
- 不存在的 habit 回傳 `404 Not Found`。
- 錯誤 response 都包含 `detail`。
