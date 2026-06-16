# 第 7 章導覽：前端開發

對應書稿：第 7 章「前端開發」  
Git tag：`ch07-frontend-local`  
本章定位：把第 3 章復古像素 RPG 靜態原型重建成 React 前端，並串接第 5 章 FastAPI 本機 API。

## 本章你會看到什麼

第 7 章開始讓讀者看到前後端整合。畫面維持第 3 章定稿的 RPG 方向：低飽和 16-bit 色盤、硬邊框、任務捲軸、金色 reward 與苔綠 action button。

本章完成後，repo 會多出：

- `frontend/`：React + Vite + TypeScript + Tailwind 前端專案。
- `frontend/src/api/client.ts`：對接 FastAPI 的 API client。
- `frontend/src/components/`：App Shell、Hero Status、Quest Log、Level Panel、Toast 與 Bottom Nav。
- `frontend/src/styles/index.css`：復古像素 RPG UI tokens 與版面。
- `tests/test_cors.py`：允許 Vite localhost origin 的 CORS 測試。
- `docs/book-assets/ch07-frontend/`：第七章可放入書稿評估的畫面截圖。

## 章節 checkpoint

讀者可以依照書本順序切換到不同小節完成時的狀態：

```bash
git checkout ch07-1-vite-foundation
git checkout ch07-2-rpg-ui-shell
git checkout ch07-3-api-integration
git checkout ch07-4-interaction-states
git checkout ch07-5-visual-qa-assets
git checkout ch07-frontend-local
```

回到最新進度：

```bash
git checkout main
git pull
```

## 本機啟動方式

先啟動後端：

```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

若 macOS 環境沒有 `python` 指令，可改用：

```bash
python3 -m uvicorn backend.app.main:app --reload --port 8000
```

再啟動前端：

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

開啟：

```text
http://127.0.0.1:5173
```

第七章刻意不做 mock fallback。若後端沒有啟動，前端會顯示復古 RPG 錯誤訊息，提醒讀者先啟動 FastAPI。

## API 串接

前端會呼叫以下 API：

- `GET /api/v1/user/profile`
- `GET /api/v1/habits`
- `POST /api/v1/habits/{habit_id}/checkin`

所有 request 會帶上 development-only token：

```http
Authorization: Bearer local-dev-token
```

環境變數範本位於 `.env.example`：

```text
VITE_API_BASE_URL=http://localhost:8000
VITE_DEV_AUTH_TOKEN=local-dev-token
```

`VITE_DEV_AUTH_TOKEN` 只用於第七章本機開發。正式登入、JWT 與註冊流程會留到後續章節。

## 前端互動狀態

第七章鎖住以下畫面狀態：

- 載入中：顯示 guild server 連線訊息。
- 成功載入：顯示 Hero Status 與 Quest Log。
- Ready habit：可點擊 `打卡領獎`。
- Done habit：顯示 `已完成`，按鈕不可點擊。
- 成功打卡：更新 EXP、gold、level 與 quest 狀態。
- Level up：後端回傳 `leveled_up=true` 時顯示 level-up panel。
- API error：顯示 RPG toast，不自行改成功狀態。
- 後端未啟動：顯示 guild server offline 提示。

## 第七章圖資

本章已產出以下截圖，供書稿評估：

| 圖號 | 檔案 |
| :--- | :--- |
| 圖 7-2-1 | `docs/book-assets/ch07-frontend/figure-7-2-1-rpg-app-shell-desktop.png` |
| 圖 7-2-2 | `docs/book-assets/ch07-frontend/figure-7-2-2-rpg-app-shell-mobile.png` |
| 圖 7-3-1 | `docs/book-assets/ch07-frontend/figure-7-3-1-api-connected-quest-log.png` |
| 圖 7-4-1 | `docs/book-assets/ch07-frontend/figure-7-4-1-checkin-success-state.png` |
| 圖 7-4-2 | `docs/book-assets/ch07-frontend/figure-7-4-2-error-toast-state.png` |

截圖使用真實 FastAPI + Vite 本機服務產生。錯誤狀態圖則刻意停掉 FastAPI 後重新整理前端，示範第七章沒有 mock fallback。

## 本章邊界

本章不做以下工作：

- 不做正式登入註冊。
- 不做 production JWT。
- 不做 Azure 部署。
- 不改 OpenAPI 契約。
- 不新增後端功能，除了本機 Vite CORS。
- 不建立遊戲引擎。

## 本章完成檢查

- [x] React + Vite + TypeScript + Tailwind 專案建立完成。
- [x] 復古像素 RPG App Shell 完成。
- [x] Hero Status 串接 profile API。
- [x] Quest Log 串接 habits API。
- [x] check-in API 串接完成。
- [x] loading、error、success、level-up、done 狀態完成。
- [x] CORS 測試完成。
- [x] 第七章書稿截圖完成。
- [x] 已建立章節 checkpoint tags。

## 下一章銜接

第 8 章會把本機專案推向雲端部署規劃。第 7 章的前端仍只面向本機 FastAPI，不包含 Azure Static Web Apps、App Service 或正式 production 環境設定。
