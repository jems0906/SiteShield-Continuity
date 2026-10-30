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
    entra_tenant_id: str = ""
    entra_client_id: str = ""
    entra_client_secret: str = ""
    entra_redirect_uri: str = ""
    auth_frontend_url: str = "http://localhost:5173/"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def entra_enabled(self) -> bool:
        return len(self.auth_secret_key) >= 32 and all((self.entra_tenant_id, self.entra_client_id, self.entra_client_secret, self.entra_redirect_uri))

settings = Settings()