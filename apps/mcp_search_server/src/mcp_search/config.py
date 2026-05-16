from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    redis_host: str = Field(..., alias="REDIS_HOST")
    redis_port: int = Field(..., alias="REDIS_PORT")

    searxng_base_url: str = Field(..., alias="SEARXNG_BASE_URL")
    request_timeout: int = Field(..., alias="REQUEST_TIMEOUT")
    max_search_results: int = Field(..., alias="MAX_SEARCH_RESULTS")
    max_crawl_pages: int = Field(..., alias="MAX_CRAWL_PAGES")
    user_agent: str = (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    )


settings = Settings()