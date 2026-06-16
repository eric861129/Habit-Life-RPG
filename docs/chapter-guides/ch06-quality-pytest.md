# 第 6 章導覽：品質保證

對應書稿：第 6 章「品質保證」  
Git tag：`ch06-quality-pytest`  
本章定位：用 Pytest 把第 5 章 FastAPI + SQLite 後端鎖成可重複驗證的品質防線。

## 本章你會看到什麼

第 6 章不新增產品功能，而是把既有後端行為轉成測試矩陣。讀者會看到如何從 User Stories、OpenAPI 契約與第五章後端程式，整理出可自動驗證的測試。

本章完成後，repo 會多出：

- `tests/conftest.py`：隔離式 SQLite 暫存資料庫、固定時間、FastAPI dependency override。
- `tests/test_user_api.py`：profile API 測試。
- `tests/test_habits_api.py`：habit list 與 check-in API 測試矩陣。
- `tests/test_rewards.py`：RPG reward service 測試。
- `docs/book-assets/ch06-quality/`：第六章圖資追蹤。

## 章節 checkpoint

讀者可以依照書本順序切換到不同小節完成時的狀態：

```bash
git checkout ch06-1-test-fixtures
git checkout ch06-2-api-contract-tests
git checkout ch06-3-reward-tests
git checkout ch06-4-docs-quality
git checkout ch06-quality-pytest
```

回到最新進度：

```bash
git checkout main
git pull
```

## 測試執行方式

安裝本機 dependencies：

```bash
python -m pip install -e ".[dev]"
```

若 macOS 環境沒有 `python` 指令，可改用：

```bash
python3 -m pip install -e ".[dev]"
```

執行測試：

```bash
python -m pytest -q
```

第六章完成時，預期會看到：

```text
15 passed
```

## 測試地基

`tests/conftest.py` 是第六章的主角。

它負責：

- 每個測試建立獨立 SQLite 暫存檔。
- 建立 `Users` / `Habits` schema。
- 用固定資料建立 user 1、user 2、habit 1、habit 2、habit 3。
- 用固定時間 `2026-06-16T09:00:00+08:00` 判斷同日打卡。
- 覆寫 FastAPI 的 `get_db` 與 `get_settings` dependency。
- 建立不執行 startup seed 的 test app。

這讓測試不會污染本機 `habit_life_rpg.db`，也不會因日期不同而忽然失敗。

## 測試矩陣

第六章鎖住以下行為：

- profile 未登入回傳 `401`。
- profile 已登入回傳玩家狀態。
- habit list 只回傳目前使用者的 habits。
- 成功打卡回傳 `200` 並更新 `current_exp`、`current_gold`、`current_level`。
- 重複打卡回傳 `400`。
- 打卡他人的 habit 回傳 `403`。
- 不存在 habit 回傳 `404`。
- 未登入打卡回傳 `401`。
- 失敗打卡不得更新玩家數值。
- reward service 固定給 `+40 EXP` 與 `+8 gold`。
- 升級時 EXP 維持累積，不歸零。

## 第六章邊界

本章不做以下工作：

- 不建立 GitHub Actions CI。
- 不建立 React app。
- 不建立 Azure 資源。
- 不建立正式登入註冊流程。
- 不建立 Alembic migration。
- 不建立完整打卡歷史表。

CI 與雲端部署會留到後續章節處理。

## 本章完成檢查

- [x] 測試資料庫隔離完成。
- [x] FastAPI test app 可關閉 startup seed。
- [x] profile API 測試完成。
- [x] habit list API 測試完成。
- [x] check-in 成功、400、401、403、404 測試完成。
- [x] reward service 測試完成。
- [x] 第六章圖資追蹤表已更新。
- [x] 已建立章節 checkpoint tags。

## 下一章銜接

第 7 章會開始建立 React + Vite 前端，並把第 5 章 API 接進復古像素 RPG 介面。第 6 章測試會在之後保護後端契約，讓前端整合時不必猜 response 欄位。
