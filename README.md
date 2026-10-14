# MLBB Tournament Pro

FastAPI + aiogram 3 + Telegram Mini App esports tournament platform.

## Quick start
1. Copy `.env.example` to `.env` and configure secrets.
2. Create a virtual environment and install `requirements.txt`.
3. Run `alembic upgrade head`.
4. Run API: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
5. Run bot separately: `python -m app.bot.main`.
6. Run tests: `pytest -q`.

## Important limitations
- MLBB identity is not verified by ID format alone. No official, authorized provider has been configured or validated in this package. Provider absence results in review status, never fabricated verification.
- Manual administrator approval is stored as `manual_approved`; it is not provider verification and is not a claim that Moonton verified the account.
- Mini App requires HTTPS in production and must be opened from the configured Telegram bot.
- This is a tested starter platform, not a complete tournament operations suite: bracket generation, result approval/ranking automation, invitation workflow, scheduled notification worker, moderation UI and complete RU/EN translations need further implementation.
