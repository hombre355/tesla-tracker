from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    tesla_client_id: str = ""
    tesla_client_secret: str = ""
    tesla_redirect_uri: str = "http://localhost:8000/api/auth/callback"
    tesla_audience: str = "https://fleet-api.prd.na.vn.cloud.tesla.com"
    tesla_auth_url: str = "https://auth.tesla.com/oauth2/v3/authorize"
    tesla_token_url: str = "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token"

    encryption_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./tesla_tracker.db"
    frontend_url: str = "http://localhost:5173"


settings = Settings()
