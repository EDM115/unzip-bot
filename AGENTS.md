# AGENTS.md - `EDM115/unzip-bot`
Rules for AI agents working in this repo

## Project snapshot (v7 rework branch)
- Language/runtime: Python `>=3.12`
- Framework: Pyrogram fork (`pyrofork`) Telegram bot
- Packaging/tooling: `uv`, `ruff`, `ty`
- Deployment: Docker (Alpine), Heroku or VPS
- Current branch state is **mid-migration**:
	- Runtime still uses legacy plugin root `modules` from `unzipbot/__init__.py`
	- New structure exists under `unzipbot/plugins/**` and `unzipbot/db/**` but parts are still WIP/empty

## Source of truth files (today)
When in doubt, prioritize these files:
- Bot startup lifecycle: `unzipbot/__main__.py`
- Client/logging setup: `unzipbot/__init__.py`
- Active handlers (legacy): `unzipbot/modules/commands.py`, `unzipbot/modules/callbacks.py`
- Current helper/data logic: `unzipbot/helpers/database.py`, `unzipbot/helpers/start.py`
- Strings/i18n: `unzipbot/i18n/**`, especially `unzipbot/i18n/lang/en.json`
- Env/config entrypoint used at runtime: root `config.py`

Migration-related files to preserve and extend (do not regress):
- DB abstraction interfaces: `unzipbot/db/orm/base.py`
- DB backends: `unzipbot/db/orm/mongodb.py`, `unzipbot/db/orm/sqlite.py`

## Quick dev workflow
- Install/refresh dependencies: `uv sync --extra dev`
- Lint + autofix: `uv run ruff check --fix`
- Format: `uv run ruff format`
- Typecheck: `uv run ty check`
- Run bot locally (with env): `python -m unzipbot` or `bash start.sh`

Docker baseline:
- Uses Alpine (`python:3.12-alpine`) and prebuilt `unrar` binary
- Keep image-size and package-compatibility constraints in mind when modifying Docker setup

## Required environment variables
At minimum, bot startup expects:
- `APP_ID`
- `API_HASH`
- `BOT_TOKEN`
- `BOT_OWNER`
- `LOGS_CHANNEL`
- `MONGODB_URL`
- `MONGODB_DBNAME` (optional default exists, but define explicitly in production)

If introducing new required variables, update:
1. `README.md` config section
2. setup/start scripts if needed
3. deployment docs (`Dockerfile`, Heroku metadata) as appropriate

## Coding rules for this repository
### 1) Keep behavior async and cancellation-safe
- Do not introduce blocking calls in handlers
- Preserve/extend task cancellation semantics (`/clean`, cancel callbacks, upload/download interruption)
- Prefer explicit state cleanup paths for canceled/failed tasks

Context from roadmap/issues: `#28`, `#245`, `#204`, `#296`

### 2) Keep functions small and composable
- Avoid giant handler functions with deeply nested logic
- Extract helper functions early when complexity grows

Context: cyclomatic complexity work from `#267` and rework goals in `#296`

### 3) Preserve i18n discipline
- User-facing text belongs in language JSON files (not hard-coded in handlers)
- Use message/button abstractions consistently
- Maintain fallback-safe behavior for untranslated keys

Context: multilingual/string rework `#179`

### 4) Path/command safety is mandatory
- Avoid unsafe shell string interpolation for file paths
- Handle spaces/special chars robustly (quote or avoid shell parsing entirely)
- Prefer subprocess arg lists over shell strings where feasible

Context: ffmpeg/ffprobe path escaping bug `#295`

### 5) Cross-filesystem compatibility
- Prefer `shutil.move` (or equivalent safe approach) over raw `os.rename` across mount boundaries

Context: Docker volumes cross-device issue `#286`

### 6) Follow DB abstraction direction
- New data work should align with interface-based backend portability
- Keep Mongo/SQLite compatibility in mind for new persistence code
- Avoid adding new one-off collection/table access patterns when a shared interface can be used

Context: `#356` (DB rework), `#401` (interfaces), roadmap `#296`

## Roadmap-aware prioritization (from #296 + linked issues)
When choosing what to work on next, prioritize unresolved **Priority S/A** roadmap items first:
- `#356` Database rework (open)
- `#204` Ongoing tasks overhaul (open)
- `#173` Unified settings page (open)
- `#245` Full cancel support for uploads/clean flow (open)
- `#169`/`#174` Better archive browsing + file tree UX (open)
- `#205` Premium/VIP system (open)

Already completed items that should **not be regressed**:
- `#249` Alpine image migration (closed)
- `#286` Volume/cross-device fix (closed)
- `#258` framework fork migration (closed)
- `#285` cron scheduling instead of sleep loop (closed)
- `#295` path escaping fix (closed)
- `#267` complexity cleanup baseline (closed)

Lower-priority but tracked:
- `#306` split archives from URLs (open)
- `#288` whitelist model (open)
- `#289` autoban strategy + privacy constraints (open)
- `#452` expose monitoring/API endpoints (open)

Legacy roadmap trackers `#38` and `#165` are closed, use `#296` as canonical planning reference

## Change-scoping guidance for agents
- If touching both legacy (`modules/**`) and new (`plugins/**`/`db/**`) trees, explain compatibility implications in the PR notes
- Do not silently migrate plugin roots or config import paths without an explicit migration plan
- Preserve bot-owner/admin command behavior unless the issue explicitly requests behavior changes

## Validation checklist before finishing work
1. `uv run ruff check --fix` & `uv run ty check` passes
2. `uv run ruff format` applied (or no formatting changes needed)
3. Startup path still valid (`python -m unzipbot` semantics not broken)
4. For task-flow changes: verify cancel/cleanup paths
5. For command execution/path changes: verify filenames with spaces
6. For DB work: verify both interface correctness and existing runtime compatibility

## Notes for future migrations
- The codebase currently contains both old and new architecture layers
- Until plugin root is switched from `modules` to `plugins`, new handlers in `plugins/**` will not be active by default
- Any migration PR should include:
	- explicit activation plan
	- backward-compat strategy
	- rollout/revert instructions
