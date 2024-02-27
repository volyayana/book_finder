from itertools import chain

from settings import settings
from store.chitay_gorod import ChitaiGorod


async def get_books_from_all_sources(search_query: str | None = ''):
    if not search_query:
        return None

    chitai_gorod = ChitaiGorod()

    unsorted_books = []
    unsorted_books.append(await chitai_gorod.get_books(search_query))

    sorted_books = [sorted(books, key=lambda x: x.price) for books in unsorted_books]
    sorted_limited_books = [books[:settings.limit_per_store] for books in sorted_books]

    return format_books_list(list(chain.from_iterable(sorted_limited_books)))


def format_books_list(books):
    formatted_list = "Список книг:\n"
    for i, book in enumerate(books, start=1):
        formatted_list += f"{i}. <b>{book.name}</b> - {book.author}\n"
        formatted_list += f"Цена: {book.price} ₽\n"
        formatted_list += f"Магазин: {book.store}\n"
        formatted_list += f"Ссылка: {book.link}\n\n"
    return formatted_list
