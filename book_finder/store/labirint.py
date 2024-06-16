import logging
from pprint import pprint

import aiohttp
import asyncio

from aiohttp_retry import RetryClient, ExponentialRetry
from bs4 import BeautifulSoup
from urllib.parse import quote

from models import Book
from config.settings import Settings
from store.abstractStore import AbstractStore
from utils import log_error


class Labirint(AbstractStore):
    def __init__(self, settings: Settings):
        self.url = 'https://www.labirint.ru'
        self.headers = {'User-agent': 'Mozilla/5.0'}
        self.params = 'order=relevance&available=1&id_genre=-1'
        self.store = 'Лабиринт'
        self.settings = settings

    async def get_books(self, search_query: str):
        books = []
        async with aiohttp.ClientSession() as session:
            retry_client = RetryClient(session)
            retry_options = ExponentialRetry(statuses=self.settings.allowed_statuses)
            async with retry_client.get(f'{ self.url }/search/{ quote(search_query) }/',
                                        headers=self.headers,
                                        params=self.params,
                                        ssl=False,
                                        retry_options=retry_options,
                                        ) as resp:
                if resp.status != 200:
                    log_error('ERROR: Labirint request status_code: %s' % resp.status)
                    return None

                logging.info('Labirint request status_code: %s' % resp.status)
                response_text = await resp.text()
                unparsed_books = self.parse_books(response_text)
                if unparsed_books is not None:
                    books = self.get_books_list(unparsed_books)
        return books

    @staticmethod
    def parse_books(text: str):
        soup = BeautifulSoup(text, "html.parser")
        not_found = soup.findAll(class_='search-error')
        if not_found:
            return None
        unparsed_books = soup.findAll(class_='product-card')
        logging.debug('Labirint found %s books by request: %s' % (len(unparsed_books), text))
        return unparsed_books

    def get_books_list(self, unparsed_books):
        books = []
        for book in unparsed_books:
            parsed_book = Book(name=book['data-name'],
                               link=f'{self.url}{book.find(class_="product-card__img")["href"]}',
                               price=float(book['data-discount-price'] or book['data-price']),
                               store=self.store,
                               )
            author = book.find(class_='product-card__author')
            if author:
                parsed_book.author = author.a['title']
            # img_src = book.find('img')
            # if img_src:
            #     parsed_book.image_url = img_src['data-src']
            books.append(parsed_book)
        return books


async def main():
    settings = Settings()
    lab_store = Labirint(settings)
    lab_books = await lab_store.get_books('мастер и маргарита')
    pprint(lab_books)


if __name__ == '__main__':
    asyncio.run(main())
