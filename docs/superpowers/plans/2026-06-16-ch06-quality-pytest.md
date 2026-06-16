# Chapter 6 Quality Pytest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan one task at a time. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Chapter 6 local Pytest quality gate for the Chapter 5 FastAPI + SQLite backend.

**Architecture:** Tests use an isolated temporary SQLite database per test and override FastAPI dependencies so they never write to the local demo database. API tests verify the Chapter 4 OpenAPI contract, while reward tests lock the Chapter 5 RPG math. Chapter 6 intentionally does not add GitHub Actions CI.

**Tech Stack:** Python 3.11+, FastAPI TestClient, Pytest, SQLAlchemy 2.x, SQLite temporary files.

---

## Scope

Included:

- Test app factory support in `backend/app/main.py`.
- Isolated pytest fixtures in `tests/conftest.py`.
- API contract tests for profile, habit list, and habit check-in.
- Reward service unit tests.
- README, chapter guide, and book asset tracking updates.
- Chapter checkpoint tags and final GitHub Release.

Excluded:

- GitHub Actions CI.
- React app.
- Azure resources.
- Formal login/register flows.
- Alembic migrations.
- Full check-in history table.

## Checkpoint Tags

| Step | Tag | Meaning |
| :--- | :--- | :--- |
| 6.1 | `ch06-1-test-fixtures` | Test isolation fixtures and app factory |
| 6.2 | `ch06-2-api-contract-tests` | API contract test matrix |
| 6.3 | `ch06-3-reward-tests` | Reward and level-up tests |
| 6.4 | `ch06-4-docs-quality` | Chapter docs and asset tracking |
| Wrap-up | `ch06-quality-pytest` | Chapter 6 complete and released |

## Implementation Tasks

1. Add `create_app(enable_startup_seed: bool = True)` so tests can disable demo seeding.
2. Add `tests/conftest.py` with:
   - `fixed_now = 2026-06-16T09:00:00+08:00`
   - one temporary SQLite file per test
   - dependency override for `get_db`
   - dependency override for `get_settings`
   - monkeypatch for the habits router clock
   - fixed users and habits: habit 1 ready, habit 2 checked in today, habit 3 owned by another user
3. Rewrite `tests/test_ch05_smoke.py` to use the shared `client` fixture.
4. Add `tests/test_user_api.py` for profile auth and response shape.
5. Add `tests/test_habits_api.py` for habit list filtering and check-in success/error scenarios.
6. Add `tests/test_rewards.py` for reward math and level-up behavior.
7. Update `pyproject.toml` to filter only the current third-party TestClient deprecation warning.
8. Update README and Chapter 6 docs.
9. Run full local verification, create tags, push, and create the GitHub Release.

## Verification Commands

```bash
git diff --check
python -m compileall backend tests
python -m pytest -q
npx --yes @redocly/cli@latest lint docs/openapi.yaml
rg -n "task""_id|Task""Id|task""Id|new""_gold|new""_exp|level""_up" README.md docs backend tests prototype
SECRET_PATTERN="sk""-[A-Za-z0-9_-]+|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY|DefaultEndpointsProtocol=|AccountKey=|password\\s*=\\s*[^\\s#]+|secret\\s*=\\s*[^\\s#]+"
rg -n --hidden -g '!docs/superpowers/plans/**' -g '!docs/book-assets/**/*.png' -g '!*.png' -g '!node_modules' -g '!dist' -g '!build' -g '!.git' "$SECRET_PATTERN" .
```

## Acceptance Criteria

- `python -m pytest -q` passes without the third-party TestClient warning in output.
- API tests cover `200`, `400`, `401`, `403`, and `404`.
- Failed check-ins do not update user `exp`, `gold`, or `level`.
- Successful check-in returns `current_exp`, `current_gold`, `current_level`, and `leveled_up`.
- No code or tests use legacy task naming or old reward response field names.
