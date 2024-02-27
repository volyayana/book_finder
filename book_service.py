from settings import settings
from store.abstractStore import AbstractStore
from store.chitay_gorod import ChitaiGorod
from store.labirint import Labirint


async def get_books_by_source(source_list: list[type[AbstractStore]], search_query: str):
    books = []
    for source in source_list:
        store = source()
        books.extend(await store.get_books(search_query))
    return books


async def get_books_from_all_sources(search_query: str | None = ''):
    if not search_query:
        return None

    sources = [ChitaiGorod, Labirint]

    unsorted_books = await get_books_by_source(sources, search_query)
    sorted_books = sorted(unsorted_books, key=lambda x: x.price)[:settings.limit_books]

    return format_books_list(sorted_books)


def format_books_list(books):
    formatted_list = "Список книг:\n"
    for i, book in enumerate(books, start=1):
        formatted_list += f"{i}. <b>{book.name}</b> - {book.author}\n"
        formatted_list += f"Цена: {book.price} ₽\n"
        formatted_list += f"Магазин: {book.store}\n"
        formatted_list += f"Ссылка: {book.link}\n\n"
    return formatted_list
