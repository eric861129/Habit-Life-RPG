# Repository Handoff

## Current project shape

- Backend: FastAPI, SQLAlchemy, SQLite local default.
- Frontend: React, Vite, TypeScript, Tailwind.
- Tests: Pytest backend tests, TypeScript production build.
- Deployment: Azure-oriented templates only; no real Azure credentials committed.

## Safe handoff steps

1. Check `git status --short`.
2. Read `README.md`.
3. Read the latest chapter guide.
4. Confirm the intended tag or milestone.
5. Run tests before editing.
6. Make changes in small commits.
7. Re-run tests and frontend build.
8. Update README progress and relevant chapter guide.

## Do not hand off

- Real secrets.
- Payment data.
- Production database credentials.
- Private user data.
- Publisher-only manuscript files.
