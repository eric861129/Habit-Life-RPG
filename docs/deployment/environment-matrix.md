# 環境矩陣

| 項目 | 本機開發 | 測試 | 正式環境 |
| --- | --- | --- | --- |
| `DATABASE_URL` | SQLite本機檔案 | 暫存SQLite | 由代管環境提供 |
| `HLR_JWT_SECRET` | 本機私密值 | 測試專用值 | 由機密管理功能提供 |
| `HLR_ACCESS_TOKEN_MINUTES` | 明確設定 | 固定測試值 | 依風險設定 |
| `HLR_APP_TIMEZONE` | `Asia/Taipei` | `Asia/Taipei` | 依服務地區設定 |
| `HLR_ALLOWED_ORIGINS` | 本機前端 | 測試來源 | 正式前端網域 |

所有值均由環境注入，真實機密不得寫入版本庫。平台選型、成本與實際部署步驟應在交付當下重新確認。
