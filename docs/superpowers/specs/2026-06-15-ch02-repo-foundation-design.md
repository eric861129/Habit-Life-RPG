# Chapter 2 Repo Foundation Design

## Goal

Establish the `Habit Life RPG` repository as a safe, chapter-versioned companion project for 《左手藍圖，右手魔法》.

## Decisions

- The repo advances on `main`.
- Reader checkpoints are preserved with Git tags and GitHub Releases.
- Chapter 2 only builds the development foundation; it must not include later chapter deliverables such as PRD, OpenAPI, backend, frontend, or cloud deployment files.
- The repo stores project documents and sanitized book assets, not the full manuscript.

## Chapter 2 Deliverables

- README with chapter progress and checkout instructions.
- `.gitignore` and `.env.example` for safe local development.
- `AGENTS.md` as the AI collaboration contract.
- Chapter guide for the toolbox stage.
- Book asset register for screenshots and diagrams.

## Acceptance Criteria

- A reader can clone the repo and understand the current chapter stage.
- No real secrets are present.
- `.env` is ignored, while `.env.example` is tracked.
- The main project contract is explicit: `Habit Life RPG`, `habit_id`, `Users`, `Habits`, and `LastCheckIn`.
- The chapter can be tagged as `ch02-toolbox`.
