from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_token: str = Field(alias='TELEGRAM_KEY')

    limit_books: int = Field(alias='LIMIT_BOOKS')


class Config:
    env_file = '.env'
    env_file_encoding = 'utf-8'


settings = Settings()  # type: ignore
