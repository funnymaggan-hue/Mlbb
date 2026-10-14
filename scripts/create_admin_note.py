"""Print configured admin IDs without exposing bot tokens."""
from app.config import settings
if __name__ == "__main__":
    print("Configured admin count:", len(settings.admin_ids))
    if len(settings.admin_ids) != 2:
        print("WARNING: ADMIN_IDS should contain exactly two Telegram IDs.")
