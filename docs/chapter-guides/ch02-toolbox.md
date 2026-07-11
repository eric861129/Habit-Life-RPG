# 第 2 章：工具箱

本章只建立安全、可追蹤、可重現的開發現場，不提前加入產品功能。

## 完成成果

- 公開 Repo 可以 clone。
- `chapter/02-toolbox` 是可獨立閱讀與驗證的章節分支。
- `.gitignore` 排除秘密、虛擬環境、套件與建置產物。
- `.env.example` 只有公開設定與明確假值。
- `scripts/verify_environment.py` 能在啟動程式前檢查必要設定。
- `AGENTS.md` 固定產品邊界、資安規則與驗證方式。
- `docs/book-assets/assets-register.md` 追蹤書稿會使用的專案畫面。

## 驗證方式

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

更換 `.env` 中的 `HLR_JWT_SECRET` 後執行：

```bash
python scripts/verify_environment.py
python -m pytest -q
```

## 本章不包含

- PRD、User Story、UX Flow 或 UI Spec。
- FastAPI、資料庫、React 或 Azure 資源。
- 真實密碼、Token、連線字串或付費設定。

下一個累進版本是 `chapter/03-blueprint`。
