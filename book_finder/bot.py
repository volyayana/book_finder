from aiogram import Bot, Dispatcher

from config.settings import Settings

import os
import logging
logging.error(os.getenv('LIMIT_BOOKS'))

settings = Settings()  # type: ignore

bot = Bot(token=settings.api_token)
dp = Dispatcher()
