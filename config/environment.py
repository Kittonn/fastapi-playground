from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
# from utils.logger import LogFormat


class Settings(BaseSettings):
  port: int = 8000
  log_format: str = "JSON"
  log_level: str = "INFO"

  model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
  return Settings()


config = get_settings()
