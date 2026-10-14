import os
os.environ.setdefault("DATABASE_URL","sqlite+aiosqlite:///./test_mlbb.db")
os.environ.setdefault("APP_SECRET_KEY","test-secret-key")
os.environ.setdefault("BOT_TOKEN","test-bot-token")
