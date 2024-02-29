from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

statuses = {x for x in range(100, 600)}
statuses.remove(200)
statuses.remove(429)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')

    api_token: str = Field(alias='TELEGRAM_KEY')
    limit_books: int = Field(alias='LIMIT_BOOKS')
    allowed_statuses: set[int] = statuses
