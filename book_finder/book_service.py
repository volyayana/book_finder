from config.settings import Settings
from store.abstractStore import AbstractStore


settings = Settings()  # type: ignore


async def get_books_from_all_sources(sources: list[AbstractStore], search_query: str | None = ''):
    if not search_query:
        return None

    unsorted_books = []
    for source in sources:
        unsorted_books.extend(await source.get_books(search_query))

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
