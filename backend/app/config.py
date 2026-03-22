from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    encryption_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./tesla_tracker.db"
    frontend_url: str = "http://localhost:5173"

    # Token refresh endpoint (no developer account required)
    tesla_token_url: str = "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token"


settings = Settings()
