import asyncio
import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ParseMode

from book_service import get_books_from_all_sources
from settings import settings

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


bot = Bot(token=settings.api_token)
dp = Dispatcher(bot)


async def process_text(message: types.Message):
    result = await get_books_from_all_sources(message.text)
    await message.reply(result, parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Привет! Я могу найти тебе книги в разных интернет-магазинах. Введи текст для поиска книги")


@dp.message_handler()
async def echo(message: types.Message):
    await process_text(message)


async def main():
    logging.info("Starting bot...")
    await dp.start_polling()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor.start_polling(dp, loop=loop, skip_updates=True)
