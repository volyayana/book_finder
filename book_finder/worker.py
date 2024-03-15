import asyncio

from celery import Celery

from config.settings import Settings
from bot import bot

settings = Settings()  # type: ignore

celery = Celery(__name__)
celery.conf.broker_url = settings.celery_url
celery.conf.result_backend = settings.celery_url


async def gather_message(error_message):
    chat = await bot.get_chat(424965357)
    await bot.send_message(chat_id=chat.id, text=error_message)


@celery.task(name="send_error_message")
def send_error_message(error_message):
    asyncio.run(gather_message(error_message))
    return True
