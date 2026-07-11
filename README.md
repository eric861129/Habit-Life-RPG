# Habit Life RPG

《左手藍圖，右手魔法》的累進式隨書範例專案。讀者可以切換公開章節分支，看到產品如何從安全的開發現場，逐步成長為部署在 Azure 的完整 MVP。

## 目前章節

| 章節 | 分支 | 本階段成果 |
| --- | --- | --- |
| 第 2 章：工具箱 | `chapter/02-toolbox` | 安全環境範本、Git 規範、AI 協作規則與可驗證開發現場 |

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

## 版本策略

- `archive/pre-rebuild-20260711`：重建前的完整舊版。
- `chapter/02-toolbox` 到 `chapter/10-agent-ready`：可直接執行的累進章節狀態。
- `book-v2-chXX-*`：與章節分支對應的不可變 Tag 與 GitHub Release。
- `main`：全書最終、已驗證且已部署的版本。

## 安全原則

不要提交密碼、JWT Secret、Azure 連線字串、部署 Token、Publish Profile 或付款資訊。任何不確定能否公開的值，先留在本機 `.env`，只將變數名稱寫入 `.env.example`。
