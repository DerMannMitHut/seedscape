# Pull Request Template

## Summary
- What does this PR change? Keep it concise.

## Motivation & Context
- Why is this needed? Reference context or prior behavior.

## Linked Issues
- Closes #<id> (use keywords: closes/fixes/resolves)

## Changes
- Key changes in bullets (APIs, models, routes, UI, config).
- Note any breaking changes or migrations.

## How to Test
- First-time setup (if needed):
  ```bash
  make install
  ```
- Format, lint, type-check, and tests:
  ```bash
  make format && make lint && make typecheck && make test
  ```
- Run locally:
  ```bash
  make dev
  # App serves frontend at http://127.0.0.1:8000/
  # API under /api (see routers in src/seedscape/api/)
  ```
- Include any specific endpoints, steps, or data needed to verify.

## Screenshots / Recordings (if UI)
- Before/after visuals or short clips.

## Notes for Reviewer (optional)
- Trade-offs, follow-ups, or areas needing special attention.

## Checklist
- [ ] I ran `make format` and `make lint`.
- [ ] I ran `make test`; all tests pass locally.
- [ ] I added/updated tests for new or changed behavior.
- [ ] I updated docs where behavior or config changed (README/AGENTS.md).
- [ ] API changes are documented (request/response, status codes, examples).
- [ ] No secrets committed; `.env`/local data not included.
- [ ] Code follows style and naming conventions (type hints, ruff clean).
- [ ] PR is focused and commit messages are clear (prefer Conventional prefixes).
- [ ] Frontend changes include screenshots and manual verification steps.
- [ ] New env vars documented with defaults (e.g., `SEEDSCAPE_DATA_DIR`).
