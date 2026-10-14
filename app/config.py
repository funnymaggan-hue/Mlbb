from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "change-this-secret"
    DATABASE_URL: str = "sqlite+aiosqlite:///./mlbb_tournament.db"
    BOT_TOKEN: str = ""
    ADMIN_IDS: str = ""
    TELEGRAM_BOT_USERNAME: str = ""
    WEBAPP_URL: str = "https://example.com"
    TELEGRAM_INITDATA_MAX_AGE: int = 86400
    PLAYER_PROVIDER_URL: str = ""
    PLAYER_PROVIDER_API_KEY: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def admin_ids(self) -> set[int]:
        try:
            return {int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()}
        except ValueError:
            return set()
settings = Settings()
