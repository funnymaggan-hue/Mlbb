from fastapi import Header, HTTPException
from app.security.telegram import validate_init_data
from app.config import settings
async def current_telegram_user(x_telegram_init_data: str | None = Header(default=None)) -> dict:
    try:
        return validate_init_data(x_telegram_init_data or "")
    except Exception as exc:
        raise HTTPException(status_code=401, detail=str(exc))
async def admin_user(user: dict = None):
    if not user or int(user["id"]) not in settings.admin_ids:
        raise HTTPException(status_code=403, detail="Administrator ruxsati kerak")
    return user
