# Repository Guidelines

## Project Structure & Modules
- `src/`: Python package entry point and modules.
  - `src/main.py`: CLI entry (`python -m src.main`).
  - `src/config/`: runtime config and env loading (`config.py`, `.env`, `.env.example`).
  - `src/services/`: business logic (`digest_service.py`).
  - `src/utils/`: helpers (`ai_utils.py`, `db_utils.py`, `telegram_utils.py`, `system_prompt.md`, `system_prompt_stage1.md`).
- `scripts/`: shell helpers (`setup.sh`, `run.sh`).
- `logs/`: runtime logs and state (e.g., `processed_entry_ids.json`).
- `requirements.txt`: Python dependencies.

## Build, Test, and Development
- Setup env: `./scripts/setup.sh` (creates `venv/` and installs deps).
- Activate venv: `source venv/bin/activate`.
- Run locally: `./scripts/run.sh [hours_back]` or `python -m src.main --hours 12 --save --debug`.
- Config: copy `src/config/.env.example` to `src/config/.env` and fill values.

## Coding Style & Naming
- Python 3.7+; 4‑space indentation; UTF‑8.
- Naming: modules/files `lower_snake_case.py`; functions/vars `lower_snake_case`; classes `PascalCase`.
- Imports: absolute within package (`from src.utils import ...`).
- Logging: use `logging` (no print) and prefer structured messages.
- Lint/format: no enforced tool; recommended locally: `black` and `ruff` (keep diffs minimal).

## Testing Guidelines
- Framework: pytest recommended (no suite in repo yet).
- Layout: place tests under `tests/` mirroring module paths, e.g., `tests/services/test_digest_service.py`.
- Naming: files `test_*.py`, functions `test_*`.
- Run: `pytest -q` (after installing pytest in venv).
- Minimum: add smoke tests for `run_digest_process(hours_back, send=False)` and for Telegram text processing; avoid network/secret use by mocking.

## Commit & Pull Requests
- Commits: concise, imperative subject (“Refactor digest generation”), with context in body if needed. Group logical changes.
- PRs: clear description, motivation, and scope; link issues; include before/after snippets or logs for digest output when relevant; note config changes; add test plan (`pytest` output or manual steps) and update README when behavior changes.

## Security & Configuration
- Do not commit secrets. `.env` lives under `src/config/` and is gitignored.
- Validate `FRESHRSS_DB_PATH` and file permissions; check `logs/` is writable.
- Telegram uses MarkdownV2; long messages are split automatically—avoid injecting unescaped special chars in new code paths.

## Behavior Overview
- Pipeline: Always two-stage.
  - Stage 1: per-article summarization in parallel (thread pool). Default workers `STAGE1_MAX_WORKERS=20`. Each article has lightweight retry (up to 2 attempts with short backoff). Failures produce empty per-article output but do not abort the stage.
  - Stage 2: global categorized digest from Stage‑1 abstracts.
- Fallbacks: If Stage 1 produces no summaries at all, or Stage 2 yields empty output, the run is considered failed (outer retry may attempt once more). Processed IDs are not updated on failure.
- Telegram: MarkdownV2 formatting with conservative escaping. No special bolding rules enforced in prompts.

## Configuration
- Set `STAGE1_MAX_WORKERS` in `src/config/.env` to control parallelism (default `20`).
- Two-stage model configuration lives in `.env`:
  - `GEMINI_STAGE2_MODEL_ID` (or legacy `GEMINI_MODEL_ID`) powers the global digest.
  - Optional `GEMINI_STAGE1_MODEL_ID` overrides the per-article summarizer; defaults to Stage 2 when omitted.
- All other behavior uses defaults from the codebase; no “mode” switch is required (single-pass removed).
