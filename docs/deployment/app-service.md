# Azure App Service Deployment Notes

## Goal

Deploy the FastAPI backend as the Chapter 8 cloud API endpoint.

## Required app settings

| Name | Example | Secret |
| :--- | :--- | :--- |
| `DATABASE_URL` | `mssql+pyodbc://...` | yes |
| `HLR_DEV_AUTH_TOKEN` | `replace-in-azure` | yes |
| `HLR_ALLOWED_ORIGINS` | `https://icy-mud-0a1b2c.azurestaticapps.net,http://localhost:5173,http://127.0.0.1:5173` | no, but environment-specific |
| `HLR_DEMO_USER_ID` | `1` | no |
| `HLR_APP_TIMEZONE` | `Asia/Taipei` | no |

## Startup command

```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## Validation

```bash
curl https://<app-service-name>.azurewebsites.net/docs
curl -H "Authorization: Bearer <token>" https://<app-service-name>.azurewebsites.net/api/v1/user/profile
```

## Notes

- This checkpoint documents the production shape; it does not commit real Azure credentials.
- For a real SQL Server connection, install and configure the required ODBC driver in the hosting environment.
- Keep CORS as an explicit whitelist through `HLR_ALLOWED_ORIGINS`.
