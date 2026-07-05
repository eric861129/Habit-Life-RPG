# Monitoring Checklist

| Area | Signal | Healthy baseline |
| :--- | :--- | :--- |
| Frontend availability | SWA homepage loads | 200 response |
| API availability | `/docs` and profile API | 200 response |
| API failures | HTTP 5xx count | zero in normal demo use |
| Auth failures | HTTP 401 count | expected only for missing token tests |
| Database | connection errors | zero |
| CORS | blocked browser requests | zero for allowed origins |

## Weekly review

- Review top API errors.
- Confirm no personal data is logged.
- Confirm secrets are still stored only in platform settings.
- Confirm GitHub Actions templates are still manual-only until real deployment is enabled.
