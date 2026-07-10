# Alerting Spec

## HTTP 5xx alert

| Field | Value |
| :--- | :--- |
| Scope | Azure App Service |
| Signal | HTTP server errors |
| Threshold | greater than 5 in 5 minutes |
| Severity | 2 |
| Action | email or Teams channel for the project owner |

## Availability alert

| Field | Value |
| :--- | :--- |
| Scope | Frontend URL and API `/docs` |
| Signal | availability test failure |
| Threshold | 2 failed checks in 5 minutes |
| Severity | 2 |
| Action | notify project owner |

## Drill record fields

- Date/time
- Alert name
- Trigger condition
- First responder
- Root cause
- Fix
- Follow-up task
