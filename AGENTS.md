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

## Verification

- Python changes: run `python -m pytest -q` and `python -m ruff check backend tests scripts` once those tools are introduced.
- Frontend changes: run `npm test -- --run` and `npm run build` from `frontend/`.
- Deployment changes: run the Azure zero-cost preflight before creating resources.
