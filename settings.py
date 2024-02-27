from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_token: str = Field(alias='TELEGRAM_KEY')

    limit_per_store: int = Field(alias='LIMIT_PER_STORE')


class Config:
    env_file = '.env'
    env_file_encoding = 'utf-8'


settings = Settings()  # type: ignore
