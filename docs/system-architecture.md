# Habit Life RPG System Architecture

## 元件

```mermaid
flowchart LR
    Browser["React / 原 Static Web Apps hostname"] -->|"HTTPS JSON"| API["FastAPI / Container Apps Consumption"]
    API -->|"SQLAlchemy"| DB[("SQLite local / Azure SQL Basic deployed")]
    API -->|"Managed Identity"| KV["Azure Key Vault"]
    Legacy["App Service B1 / 48h rollback"] -.-> DB
    Actions["GitHub Actions"] --> Browser
    Actions -->|"OIDC deploy"| API
    Actions -->|"SHA image"| GHCR["Public GHCR / no secrets"]
    GHCR --> API
```

- React 只管理互動與顯示，不計算獎勵。
- FastAPI 驗證 JWT、資料所有權、日期與商業規則。
- SQLite 讓讀者本機零設定啟動；Azure SQL 是正式教學部署資料庫。
- SQLAlchemy 模型與 Alembic migration 是兩個環境的共同契約。
- GitHub Actions 在部署前執行後端、前端、契約測試與 container vulnerability scan。
- Container Apps 無流量時可 scale to zero；SQL Basic 仍是主要固定月費。

## 信任邊界

- 瀏覽器輸入一律不可信。
- JWT 只證明身分，Habit 查詢仍必須包含 `user_id`。
- Runtime secret 只存在本機 `.env`／既有 App Settings 與 Azure Key Vault；GitHub Environment 只保存 Static Web Apps deployment token，Azure 登入使用 OIDC，不保存 client secret。
- Public GHCR image 只包含可公開的程式與 runtime dependency，不包含 `.env`、Connection String、JWT secret 或 Azure credential。
- CORS 只列出本機開發來源與最後部署的 Static Web Apps 來源。

## 章節演進

第 4 章固定資料與 API 契約；第 5 章實作 FastAPI；第 6 章建立品質防線；第 7 章建立 React；第 8 章才建立 Azure 資源。
