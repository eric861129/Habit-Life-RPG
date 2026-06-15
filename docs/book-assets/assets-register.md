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

## 核對方式

每次新增圖片後，請確認：

- [ ] 圖片檔案名稱包含圖號。
- [ ] 圖片已遮蔽敏感資訊。
- [ ] 本表狀態已更新。
- [ ] 對應章節導覽文件或 README 已能引導讀者找到圖片。
