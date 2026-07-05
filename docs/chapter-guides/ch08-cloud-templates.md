# 第 8 章導覽：雲端部署範本

對應書稿：第 8 章「雲端部署」  
Git tag：`ch08-cloud-templates`  
本章定位：把第 7 章的本機前後端整理成可部署到 Azure 的文件與範本，不提交任何真實 Azure secret。

## 本章交付物

- `docs/deployment/azure-sql-schema.sql`：把 SQLite MVP 結構轉成 Azure SQL 可讀的 T-SQL 草案。
- `docs/deployment/app-service.md`：Azure App Service 後端部署設定。
- `docs/deployment/static-web-apps.md`：Azure Static Web Apps 前端部署設定。
- `docs/deployment/environment-matrix.md`：本機、App Service、SWA 的環境變數對照。
- `.github/workflows/azure-app-service-template.yml`：手動觸發的後端部署 workflow 範本。
- `.github/workflows/azure-static-web-apps-template.yml`：手動觸發的前端部署 workflow 範本。
- `.env.example`：補上 `HLR_ALLOWED_ORIGINS` 與 Azure 設定名稱範例。

## 部署順序

1. 建立 Azure Resource Group。
2. 建立 Azure SQL Database，先用 `docs/deployment/azure-sql-schema.sql` 建表。
3. 建立 Azure App Service，設定 `DATABASE_URL`、`HLR_DEV_AUTH_TOKEN`、`HLR_ALLOWED_ORIGINS`。
4. 建立 Azure Static Web Apps，設定 `VITE_API_BASE_URL` 與 `VITE_DEV_AUTH_TOKEN`。
5. 更新後端 CORS 白名單，確認正式 SWA URL 可以呼叫 API。
6. 使用 GitHub Actions workflow 範本建立可重跑部署流程。

## 安全邊界

- 不提交 Azure connection string、publish profile、SWA token、真實 JWT secret。
- `.env.example` 只放變數名稱與假值。
- workflow 範本只引用 GitHub Secrets 名稱，不包含任何秘密值。
- `HLR_DEV_AUTH_TOKEN` 仍是教學用 development token，不是 production auth。

## 驗證指令

```bash
python -m pytest -q
cd frontend
npm run build
```

## 本章完成檢查

- [x] Azure SQL schema 草案完成。
- [x] App Service 設定文件完成。
- [x] Static Web Apps 設定文件完成。
- [x] CORS 可由 `HLR_ALLOWED_ORIGINS` 設定。
- [x] GitHub Actions 範本完成且不自動在 push 時執行。
- [x] `.env.example` 無真實 secret。
