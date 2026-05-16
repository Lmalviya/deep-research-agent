from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)

    # Database Config (loaded from .env)
    litellm_base_url: str = Field(..., alias="LITELLM_BASE_URL")
    litellm_api_key: str = Field(..., alias="LITELLM_API_KEY")

settings = Settings()
