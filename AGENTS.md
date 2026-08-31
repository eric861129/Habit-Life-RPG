# Habit Life RPG collaboration rules

## Product boundary

- Build the book MVP: authentication, habit CRUD, daily check-in, streaks, gold, experience, levels, and a personal dashboard.
- Do not add shops, bosses, social features, or unrelated game systems.
- Keep chapter branches cumulative and runnable.

## Engineering rules

- Treat `docs/` as the product and architecture contract.
- Write a failing test before behavior changes, then implement the smallest coherent fix.
- Keep SQLite available for local learning and Azure SQL compatibility for deployment.
- Never commit `.env`, credentials, tokens, publish profiles, or connection strings.
- Do not weaken authentication, authorization, CORS, or database constraints to make a test pass.
- Do not rewrite published chapter branches, tags, or releases.
- Keep Azure on Static Web Apps Free, Azure Container Apps Consumption with `minReplicas: 0`, `maxReplicas: 2`, and Azure SQL Basic 5 DTU with 2 GB. App Service B1 is only the explicitly time-bounded rollback path during migration. Keep the resource-group monthly Budget at approximately US$30; never substitute a higher paid SKU or add a fixed-cost service without explicit approval.
- Treat public URLs, chapter branches, Tags, Releases, the Runbook, and the privacy policy as reader-facing contracts.

## Verification

- Python changes: run `python -m pytest -q` and `python -m ruff check backend tests scripts` once those tools are introduced.
- Frontend changes: run `npm test -- --run` and `npm run build` from `frontend/`.
- Deployment changes: run the Azure paid-budget preflight, container security checks, and review Bicep what-if before changing resources. Never cut over the frontend API URL until the side-by-side Container App passes health and reader-journey verification.
- Final handoff: run `python scripts/final_verify.py` and report the exact failing layer if it does not pass.
- Use `python scripts/final_verify.py --skip-live` for offline work; never replace the live release check with the offline result.
