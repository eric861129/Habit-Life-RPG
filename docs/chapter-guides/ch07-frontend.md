# 第 7 章：前端開發

`chapter/07-frontend` 在第 6 章品質閘門之上加入 React 前端，完成書中 Habit Life RPG 的可操作 MVP。

## 啟動順序

1. 在專案根目錄安裝 Python 依賴，執行 `alembic upgrade head`。
2. 啟動 `python -m uvicorn backend.app.main:app --reload --port 8000`。
3. 在 `frontend/` 執行 `cp .env.example .env`、`npm ci`與 `npm run dev`。
4. 開啟 `http://localhost:5173`，註冊一個測試帳號。

## 讀者可驗收的功能

- 註冊、登入、登出與通行憑證過期回登入頁。
- 讀取角色的 Level、EXP、gold 與今日完成進度。
- 新增、編輯、封存 Habit。
- 每個 Habit 每日只能 Check-in 一次。
- Check-in 後立即顯示 Streak、`+40 EXP` 與 `+8 gold`。
- 桌面與 390px 手機寬度皆無水平溢出。

## 前端品質閘門

```bash
cd frontend
npm test -- --run
npm run build
```

Vitest 覆蓋註冊、登入、空狀態、新增 Habit 與 Check-in 回饋。GitHub Actions 在檢測到 `frontend/package-lock.json` 後，會自動執行安裝、測試與正式建置。

下一個累進版本是 `chapter/08-deployment`。
