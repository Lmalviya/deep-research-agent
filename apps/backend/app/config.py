from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)

    # Database Config (loaded from .env)
    backend_db_user: str = Field(..., alias="BACKEND_DB_USER")
    backend_db_password: str = Field(..., alias="BACKEND_DB_PASSWORD")
    backend_db_endpoint: str = Field(..., alias="BACKEND_DB_ENDPOINT")
    backend_db_port: int = Field(..., alias="BACKEND_DB_PORT")
    backend_db_name: str = Field(..., alias="BACKEND_DB_NAME")

    # Token encryption key (Fernet)
    secret_key: str = Field(..., alias="SECRET_KEY")

    # Brain service URL
    brain_url: str = Field(..., alias="BRAIN_URL")

    # CORS — comma-separated origins
    cors_origins: str = Field(..., alias="CORS_ORIGINS")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.backend_db_user}:"
            f"{self.backend_db_password}@"
            f"{self.backend_db_endpoint}:"
            f"{self.backend_db_port}/"
            f"{self.backend_db_name}"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

settings = Settings()
