# Agent-ready Guide

## What an Agent can safely do

- Read existing docs before editing.
- Propose an implementation plan.
- Modify code in a feature branch.
- Add or update tests.
- Run `python -m pytest -q`.
- Run `npm run build` in `frontend`.
- Summarize risks before deployment.

## What requires human approval

- Changing authentication strategy.
- Changing production database schema.
- Adding new personal data fields.
- Enabling automatic deployment workflows.
- Rotating or reading secrets.
- Publishing a GitHub Release.

## Minimum prompt for future work

```text
Read README.md, AGENTS.md, docs/chapter-guides, and the relevant source files first.
Create a plan before editing.
Do not commit secrets.
Run backend tests and frontend build before reporting done.
```
