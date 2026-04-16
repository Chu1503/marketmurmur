from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    database_url: str
    news_api_key: str = ""
    guardian_api_key: str = ""
    environment:  str = "development"
    debug:        bool = True
    app_name:     str = "MarketMurmur"
    app_version:  str = "1.0.0"

    @property
    def clean_database_url(self) -> str:
        url = self.database_url
        url = url.replace("?pgbouncer=true", "")
        url = url.replace("&pgbouncer=true", "")
        return url

    class Config:
        env_file     = str(ENV_FILE)
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()