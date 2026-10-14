import hashlib, hmac, time
from urllib.parse import parse_qsl
from app.config import settings
def validate_init_data(init_data: str, bot_token: str | None = None, max_age: int | None = None) -> dict:
    token = bot_token if bot_token is not None else settings.BOT_TOKEN
    if not token or not init_data:
        raise ValueError("Telegram autentifikatsiya ma’lumoti mavjud emas")
    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise ValueError("initData hash topilmadi")
    auth_date = int(pairs.get("auth_date", "0"))
    age = int(time.time()) - auth_date
    if age < -60 or age > (max_age or settings.TELEGRAM_INITDATA_MAX_AGE):
        raise ValueError("Telegram initData eskirgan")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    calculated = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calculated, received_hash):
        raise ValueError("Telegram initData imzosi noto‘g‘ri")
    import json
    user = json.loads(pairs.get("user", "{}"))
    if not user.get("id"):
        raise ValueError("Telegram user ID topilmadi")
    return user
