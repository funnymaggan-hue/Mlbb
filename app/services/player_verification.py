import re, httpx
from app.config import settings
ID_RE = re.compile(r"^[0-9]{5,15}$")
SERVER_RE = re.compile(r"^[0-9]{1,6}$")
def validate_format(mlbb_id: str, server_id: str) -> bool:
    return bool(ID_RE.fullmatch(mlbb_id.strip()) and SERVER_RE.fullmatch(server_id.strip()))
async def query_provider(mlbb_id: str, server_id: str) -> dict:
    """Only trusts an explicitly configured provider; never fabricates verification."""
    if not settings.PLAYER_PROVIDER_URL:
        return {"status": "unverified", "reason": "Tasdiqlangan provayder sozlanmagan"}
    headers = {"Accept": "application/json"}
    if settings.PLAYER_PROVIDER_API_KEY:
        headers["Authorization"] = f"Bearer {settings.PLAYER_PROVIDER_API_KEY}"
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=False) as client:
            response = await client.get(settings.PLAYER_PROVIDER_URL, params={"user_id": mlbb_id, "server_id": server_id}, headers=headers)
        if response.status_code != 200:
            return {"status": "provider_error", "reason": f"Provayder HTTP {response.status_code}"}
        data = response.json()
        # Require an explicit, documented contract; do not treat HTTP 200 as proof.
        if str(data.get("user_id", "")) != mlbb_id or str(data.get("server_id", "")) != server_id or not data.get("nickname"):
            return {"status": "unverified", "reason": "Provayder javobi identifikatorlarni ishonchli tasdiqlamadi"}
        return {"status": "verified", "nickname": str(data["nickname"]), "provider": "configured_provider"}
    except (httpx.HTTPError, ValueError, TypeError):
        return {"status": "provider_error", "reason": "Provayderga ulanish yoki javobni o‘qish xatosi"}
