---
name: hlr-release
description: Verify and publish a cumulative Habit Life RPG book chapter without weakening tests, security, public links, or Azure zero-cost guards.
---

# HLR Release

1. Read `AGENTS.md`, the target `docs/chapter-guides/` file, and `docs/final-checklist.md`.
2. Confirm the work is cumulative from the preceding published chapter and contains no credentials.
3. Run `python scripts/final_verify.py`; fix the first failing layer before continuing.
4. For infrastructure changes, run Azure preflight and Bicep what-if. Stop if estimated cost is not zero, SQL is not `AutoPause`, or any paid SKU appears.
5. Confirm the chapter branch and `book-v2-chXX-*` Tag point to the same tested commit.
6. Verify the branch and Release through anonymous HTTPS before updating reader-facing links.

Never rewrite a published chapter branch, Tag, Release, or the archive branch. Never deploy by bypassing the test job or by placing a long-lived Azure secret in GitHub.
