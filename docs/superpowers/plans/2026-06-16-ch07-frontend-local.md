# Chapter 7 Frontend Local Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan one task at a time. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Chapter 7 local React + Vite + TypeScript frontend for Habit Life RPG and connect it to the Chapter 5 FastAPI API.

**Architecture:** The frontend lives in `frontend/` and uses a code-native React app, not the Chapter 3 static HTML file. Chapter 3 `docs/ui-spec.md` and `prototype/static/index.html` are the accepted visual spec: retro pixel RPG, quest scrolls, hard borders, muted 16-bit palette, and no modern neon dashboard. The frontend requires the FastAPI backend to be running; no mock fallback is provided.

**Tech Stack:** React, Vite, TypeScript, Tailwind CSS, Vitest, React Testing Library, Playwright screenshots for book assets, FastAPI CORS for localhost Vite origins.

---

## Checkpoint Tags

| Step | Tag | Meaning |
| :--- | :--- | :--- |
| 7.1 | `ch07-1-vite-foundation` | React + Vite + TS + Tailwind foundation and backend CORS |
| 7.2 | `ch07-2-rpg-ui-shell` | Retro RPG app shell rebuilt from Chapter 3 |
| 7.3 | `ch07-3-api-integration` | Profile, habits, and check-in API integration |
| 7.4 | `ch07-4-interaction-states` | Loading, error, success, level-up, and done states |
| 7.5 | `ch07-5-visual-qa-assets` | Playwright screenshots, docs, and asset tracking |
| Wrap-up | `ch07-frontend-local` | Chapter 7 complete and released |

## Implementation Tasks

1. Create `frontend/` with Vite React TypeScript, Tailwind, Vitest, and Testing Library.
2. Add FastAPI `CORSMiddleware` for `http://localhost:5173` and `http://127.0.0.1:5173`, plus a backend CORS test.
3. Rebuild the Chapter 3 static prototype as React components with CSS variables and Tailwind utilities.
4. Add typed API client using `VITE_API_BASE_URL` and `VITE_DEV_AUTH_TOKEN`.
5. Implement real profile/habit loading and check-in mutation against FastAPI.
6. Add interaction states: loading, API unavailable, error toast, success toast, level-up panel, disabled done buttons.
7. Add frontend unit tests for rendering, check-in success, and API error handling.
8. Generate Playwright desktop/mobile/state screenshots into `docs/book-assets/ch07-frontend/`.
9. Update README, chapter guide, asset register, tags, and GitHub Release.

## Verification Commands

```bash
git diff --check
python -m compileall backend tests
python -m pytest -q
cd frontend && npm run build
cd frontend && npm run test
npx --yes @redocly/cli@latest lint docs/openapi.yaml
rg -n "task""_id|Task""Id|task""Id|new""_gold|new""_exp|level""_up" README.md docs backend tests frontend prototype
SECRET_PATTERN="sk""-[A-Za-z0-9_-]+|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY|DefaultEndpointsProtocol=|AccountKey=|password\\s*=\\s*[^\\s#]+|secret\\s*=\\s*[^\\s#]+"
rg -n --hidden -g '!docs/superpowers/plans/**' -g '!docs/book-assets/**/*.png' -g '!*.png' -g '!node_modules' -g '!dist' -g '!build' -g '!.git' "$SECRET_PATTERN" .
```

## Acceptance Criteria

- Frontend uses TypeScript and runs from `frontend/`.
- The local frontend requires the backend; it does not include mock fallback data.
- UI copy may say Quest/Hero/Reward, but code/API/types use `habit` names.
- The UI visually follows Chapter 3 retro pixel RPG spec.
- Check-in updates the displayed profile and habit state from API responses.
- Desktop and mobile screenshots are saved for book review.
