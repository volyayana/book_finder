import asyncio
import logging

import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry

from pprint import pprint

from models import Book
from config.settings import Settings
from store.abstractStore import AbstractStore


class ChitaiGorod(AbstractStore):
    def __init__(self, settings: Settings):
        self.store = 'Читай город'
        self.api_url = 'https://web-gate.chitai-gorod.ru/api/v2/search/product'
        self.book_url = 'https://www.chitai-gorod.ru'
        self.image_url = 'https://content.img-gorod.ru'
        self.access_token = None
        self.settings = settings

    async def pre_request(self):
        headers = {'User-agent': 'Mozilla/5.0'}
        async with aiohttp.ClientSession() as session:
            retry_client = RetryClient(session)
            retry_options = ExponentialRetry(statuses=self.settings.allowed_statuses)
            async with retry_client.get(self.book_url,
                                        headers=headers,
                                        ssl=False,
                                        retry_options=retry_options,
                                        ) as resp:
                try:
                    logging.debug('ChitaiGorod pre-request status_code: %s' % resp.status)
                    cookies = session.cookie_jar.filter_cookies(self.book_url)
                    self.access_token = cookies['access-token'].value.replace('%20', ' ')
                except KeyError:
                    logging.error('Error occurred during ChitaiGorod pre-request %s' % resp.status)
                finally:
                    await retry_client.close()

    async def get_books(self, search_query: str):
        # pre-request only to get cookies with token
        if self.access_token is None:
            await self.pre_request()
            if self.access_token is None:
                return []

        # sleep to emulate user
        await asyncio.sleep(1)

        headers = {
            'Authorization': self.access_token,
        }
        params = {
            'phrase': search_query,
            'products[page]': 1,
            'products[per-page]': 48,
            'sortPreset': 'relevance',
            'filters[onlyAvailable]': 1,
        }
        async with aiohttp.ClientSession() as session:
            retry_client = RetryClient(session)
            retry_options = ExponentialRetry(statuses=self.settings.allowed_statuses)
            async with retry_client.get(self.api_url,
                                        headers=headers,
                                        params=params,
                                        ssl=False,
                                        retry_options=retry_options,
                                        ) as resp:
                books = await resp.json()
                if books:
                    books = self.get_parsed_books(books)
        return books

    def get_parsed_books(self, book_json):
        books = []
        books_result = book_json.get('included')
        if books_result:
            books = [
                Book(author=self.get_authors(book['attributes']),
                     name=book['attributes']['title'],
                     link=f'{self.book_url}/{book["attributes"]["url"]}',
                     price=book['attributes']['price'],
                     store=self.store,
                     image_url=f'{self.image_url}/{book["attributes"]["picture"]}?width=400&height=560&fit=bounds'
                     )
                for book in books_result if book['type'] == 'product'
            ]
        return books

    @staticmethod
    def get_authors(book):
        authors = book.get('authors')
        if not authors:
            return ''
        str_authors = [f'{a["firstName"]} {a["middleName"]} {a["lastName"]}' for a in authors]
        return ', '.join(str_authors)


async def main():
    cg_store = ChitaiGorod()
    cg_books = await cg_store.get_books('мастер и маргарита')
    pprint(cg_books)


if __name__ == '__main__':
    asyncio.run(main())
