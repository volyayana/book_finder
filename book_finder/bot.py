from aiogram import Bot, Dispatcher

from config.settings import Settings

settings = Settings()  # type: ignore

bot = Bot(token=settings.api_token)
dp = Dispatcher()
