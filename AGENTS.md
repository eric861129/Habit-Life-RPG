# AGENTS.md

本檔是《左手藍圖，右手魔法》隨書範例專案的 AI 協作規則。所有 AI 工具、Agent、CLI 助手在修改本專案前，都應先閱讀本檔。

## 專案定位

- 專案名稱：`Habit Life RPG`
- 用途：示範文件驅動開發（Document-Driven Development, DDD）如何帶領 AI 建築團隊完成一個習慣養成 RPG App。
- Repository 會跟著書本章節逐步演進，不可一次提前加入後面章節的完整成品。

## 章節進度規則

1. 每個章節 checkpoint 都必須能讓讀者理解「目前做到哪裡」。
2. 不要在第 2 章 checkpoint 提前加入第 5 章後端、第 7 章前端或第 8 章雲端部署成品。
3. 每個重要 checkpoint 使用 Git tag 與 GitHub Release 保留。
4. 每次變更都要更新 README 的進度表或對應章節導覽文件。

## 主線契約

- 核心案例：`Habit Life RPG`
- 核心 API：`POST /api/v1/habits/{habit_id}/checkin`
- 進入系統語言後，一律使用 `habit` / `habits` / `habit_id`，不要混用 `task_id`。
- MVP 資料模型以 `Users` 與 `Habits` 為核心。
- MVP 中「同日不可重複打卡」以 `Habits.LastCheckIn` 示範。

## 安全底線

- 不可提交 `.env`。
- 不可提交真實 API Key、JWT secret、Azure connection string、密碼、付款資訊或個資。
- 密碼資料只能以 `PasswordHash` 或等價欄位呈現，不可儲存明文密碼。
- 截圖放入 `docs/book-assets/` 前必須遮蔽帳號、Email、訂閱 ID、token、secret 與付款資訊。

## AI 施工規則

- 大型修改前先提出 Plan，不要直接改碼。
- 修改應只涵蓋當前章節或當前任務。
- 如果文件與程式碼衝突，先停下來指出衝突，不要自行通靈補完。
- 程式碼章節開始後，測試與驗證要跟著章節一起建立。

## 禁止操作

禁止批量刪除文件或目錄。

不要使用：

- `del /s`
- `rd /s`
- `rmdir /s`
- `Remove-Item -Recurse`
- `rm -rf`

需要刪除文件時，只能一次刪除一個明確路徑的文件。若需要批量刪除，停止操作並請使用者手動處理。
