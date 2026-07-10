# Azure Static Web Apps Deployment Notes

## Goal

Deploy the React/Vite frontend and point it at the App Service backend.

## Required settings

| Name | Example |
| :--- | :--- |
| `VITE_API_BASE_URL` | `https://habit-life-api.azurewebsites.net` |
| `VITE_DEV_AUTH_TOKEN` | `replace-in-azure` |
| `VITE_APPINSIGHTS_CONNECTION_STRING` | optional |

## Build settings

| Field | Value |
| :--- | :--- |
| App location | `frontend` |
| Output location | `dist` |
| Build command | `npm run build` |

## Validation

1. Open the SWA URL.
2. Confirm the homepage loads.
3. Use browser Network tools to verify requests go to `VITE_API_BASE_URL`, not `localhost`.
4. Confirm App Service CORS allows the SWA origin.
