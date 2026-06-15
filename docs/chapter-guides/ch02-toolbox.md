# 第 2 章：工具箱 Repo 基礎

本章目標是替 `Habit Life RPG` 建立安全、可追蹤、可隨書演進的開發現場。

第 2 章不實作產品功能，不建立後端 API，也不建立 React 前端。這個 checkpoint 專注在「讀者可以安全開始跟著書做」。

## 對應書稿

- 2.1 開發基地建置與 AI 燃料選擇
- 2.2 AI 建築團隊：不同角色的職責分工與切換時機
- 2.3 圖資室：建立專屬的 AI 知識庫
- 2.4 版本控制與專案回復機制
- 2.5 開發環境安全保險箱
- 2.6 怎麼寫好 Prompt

## 本章完成內容

- GitHub repo 已建立並可被 clone。
- README 說明章節式版本進度與 checkout 方法。
- `.gitignore` 排除機密與本機產物。
- `.env.example` 提供安全的環境變數範本。
- `AGENTS.md` 固定 AI 協作規則與主線契約。
- `docs/book-assets/assets-register.md` 建立圖片素材追蹤表。

## 本章不做的事

- 不建立 `docs/PRD.md`。
- 不建立 `docs/openapi.yaml`。
- 不建立 FastAPI 後端。
- 不建立 React 前端。
- 不放任何真實 secret。

## 讀者檢查清單

- [ ] 我能 clone repo。
- [ ] 我知道如何用 `git checkout ch02-toolbox` 回到本章狀態。
- [ ] 我知道 `.env` 不可提交。
- [ ] 我能用 `.env.example` 建立自己的本機 `.env`。
- [ ] 我知道後續每章都會用 tag / release 保留進度。

## 建議 Git tag

```bash
git tag ch02-toolbox
git push origin ch02-toolbox
```
