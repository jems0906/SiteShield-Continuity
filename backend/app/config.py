from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./siteshield.db"
    cors_origins: str = "http://localhost:5173"
    demo_mode: bool = True
    allow_demo_reset: bool = False
    auth_secret_key: str = ""
    auth_session_seconds: int = 1800
    auth_cookie_secure: bool = False
    auth_cookie_samesite: str = "lax"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()