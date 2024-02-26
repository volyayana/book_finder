from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    api_token: str = Field(..., env='TELEGRAM_KEY')

    limit_per_store: int = Field(..., env='LIMIT_PER_STORE')


class Config:
    env_file = '.env'
    env_file_encoding = 'utf-8'


settings = Settings()
