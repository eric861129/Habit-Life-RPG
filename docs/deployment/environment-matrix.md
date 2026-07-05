# Environment Matrix

| Setting | Local | Azure App Service | Azure Static Web Apps | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./habit_life_rpg.db` | Secret app setting | n/a | Do not commit production connection strings. |
| `HLR_DEV_AUTH_TOKEN` | `local-dev-token` | Secret app setting | n/a | Teaching token only; replace for real production auth. |
| `HLR_ALLOWED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | SWA production URL plus local dev URLs | n/a | Keep this as a comma-separated whitelist. |
| `HLR_DEMO_USER_ID` | `1` | `1` or seeded user id | n/a | Demo data only. |
| `HLR_APP_TIMEZONE` | `Asia/Taipei` | `Asia/Taipei` | n/a | Used for check-in date boundaries. |
| `VITE_API_BASE_URL` | `http://localhost:8000` | n/a | App Service API URL | Set in SWA build/runtime settings. |
| `VITE_DEV_AUTH_TOKEN` | `local-dev-token` | n/a | Secret/static app setting | Must match the backend teaching token. |
| `VITE_APPINSIGHTS_CONNECTION_STRING` | blank | n/a | Optional setting | Do not send personal data in telemetry. |

## Production checklist

- App Service settings contain real values.
- Static Web Apps settings point to the App Service URL.
- Backend CORS does not use `*`.
- No connection string or token appears in git history.
