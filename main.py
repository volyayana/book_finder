import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

from book_service import get_books_from_all_sources
from settings import settings

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


bot = Bot(token=settings.api_token)
dp = Dispatcher()


async def process_text(message: types.Message):
    result = await get_books_from_all_sources(message.text)
    if result:
        await message.reply(result, parse_mode=ParseMode.HTML)


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.reply("Привет! Я могу найти тебе книги в разных интернет-магазинах. Введи текст для поиска книги")


@dp.message(F.text)
async def echo(message: types.Message):
    await process_text(message)


@dp.message(~F.text)
async def echo_non_text(message: types.Message):
    await message.reply("К сожалению, я понимаю только текст. Введи новый запрос")


async def main():
    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(main())
