import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

from book_service import get_books_from_all_sources
from config.settings import Settings

from store.chitai_gorod import ChitaiGorod
from store.labirint import Labirint

settings = Settings()  # type: ignore
logging.basicConfig(level=logging.INFO)


bot = Bot(token=settings.api_token)
dp = Dispatcher()


sources = [ChitaiGorod(settings), Labirint(settings)]


async def process_text(message: types.Message):
    result = await get_books_from_all_sources(sources, message.text)
    if result:
        await message.reply(
            result,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )


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
