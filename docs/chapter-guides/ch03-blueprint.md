# 第 3 章導覽：藍圖定稿

對應書稿：第 3 章「藍圖繪製」  
Git tag：`ch03-blueprint`  
本章定位：把產品想法整理成可交給 AI 建築團隊施工的文件藍圖。

## 本章你會看到什麼

第 3 章仍然不進入正式程式開發。這一章的任務，是把 `Habit Life RPG` 從一句「習慣養成 RPG App」拆成可討論、可驗收、可交給後續章節施工的文件。

本章完成後，repo 會多出：

- `docs/PRD.md`：產品需求文件，定義 MVP 範圍、產品規則與技術路線。
- `docs/user-stories.md`：使用者故事與驗收標準，鎖定打卡主循環。
- `docs/ux-flow.md`：Mermaid UX Flow，視覺化登入、打卡、成功、失敗與升級分支。
- `docs/ui-spec.md`：復古像素 RPG 風格 UI Spec，定義 Hero Status、任務捲軸式 Quest Log、Reward 與底部導覽。
- `prototype/static/index.html`：純 HTML/CSS 靜態原型，不接 API、不使用 JavaScript。
- `docs/book-assets/ch03-blueprint/`：可評估放入書稿的第三章截圖。

## 章節 checkpoint

讀者可以依照書本順序切換到不同小節完成時的狀態：

```bash
git checkout ch03-1-prd
git checkout ch03-2-user-stories
git checkout ch03-3-ux-flow
git checkout ch03-4-ui-spec-static
git checkout ch03-blueprint
```

回到最新進度：

```bash
git checkout main
git pull
```

## 本章主線

### 3.1 PRD

`docs/PRD.md` 是本專案的產品憲法。

請特別注意：

- MVP 只做 habit 打卡、伺服器端獎勵結算、等級成長與懲罰機制。
- BOSS 戰、屬性配點、番茄鐘、看板與月曆都不在本書主線完整實作。
- 技術路線先用 FastAPI + SQLite 跑通本機 MVP，後面再升級到 Azure SQL。

### 3.2 User Stories

`docs/user-stories.md` 把 PRD 拆成可驗收的故事。

核心故事是：

```http
POST /api/v1/habits/{habit_id}/checkin
```

驗收標準已先定義：

- 成功打卡回傳 `200 OK`。
- 同日重複打卡回傳 `400 Bad Request`。
- 打卡他人的 habit 回傳 `403 Forbidden`。
- 未登入回傳 `401 Unauthorized`。
- habit 不存在回傳 `404 Not Found`。

### 3.3 UX Flow

`docs/ux-flow.md` 用 Mermaid 把主流程畫出來。

這份圖的價值不是漂亮，而是讓後續章節可以清楚看到：

- 登入狀態如何分流。
- 打卡 API 成功與失敗如何分流。
- 升級狀態如何回到首頁。
- 錯誤狀態不應更新成功 UI。

### 3.4 復古像素 RPG UI Spec 與靜態原型

`docs/ui-spec.md` 與 `prototype/static/index.html` 讓讀者先看到產品雛形。

這裡要注意一個重要邊界：

- UI 可以把 habit 包裝成 `Quest`，並讓每個 habit item 像任務捲軸，讓畫面更有復古 RPG 感。
- 但 API、資料表、測試與程式碼仍然使用 `habit` / `habits` / `habit_id`。
- 第三章不做 Phaser、Three.js、canvas playfield 或遊戲引擎。
- 第三章只示範遊戲化 UI，不提前做正式 React 前端。

## 可評估書稿圖片

第三章已先輸出多張 `圖 3-4-2` 候選截圖：

- `docs/book-assets/ch03-blueprint/figure-3-4-2-static-prototype-desktop.png`
- `docs/book-assets/ch03-blueprint/figure-3-4-2-static-prototype-mobile.png`
- `docs/book-assets/ch03-blueprint/figure-3-4-2-static-prototype-core-ui.png`
- `docs/book-assets/ch03-blueprint/figure-3-4-2-hero-status-rpg-ui.png`
- `docs/book-assets/ch03-blueprint/figure-3-4-2-quest-log-rpg-ui.png`

這些圖目前狀態是 `drafted`，代表可以評估排版與內容，但正式交稿前仍可再裁切、加註或重截。

## 本章完成檢查

- [x] PRD 已建立。
- [x] User Stories 與 AC 已建立。
- [x] UX Flow Mermaid 已建立。
- [x] RPG UI Spec 已建立。
- [x] 靜態原型已建立。
- [x] 第三章圖資追蹤表已更新。
- [x] 已建立章節 checkpoint tags。

## 下一章銜接

第 4 章會從產品語言進入系統語言。

下一章要把本章文件轉成：

- 系統架構圖。
- 資料庫 ERD。
- API Spec / OpenAPI 契約。
- 後端資料模型與路由規劃。

請不要跳過本章文件直接寫程式。第 4 章之所以能穩，是因為第 3 章已經先把產品邊界畫清楚。
