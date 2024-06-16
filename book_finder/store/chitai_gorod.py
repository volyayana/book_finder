import asyncio
import logging
from http import HTTPStatus

import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry

from pprint import pprint

from models import Book
from config.settings import Settings
from store.abstractStore import AbstractStore
from utils import log_error


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
                logging.debug('ChitaiGorod pre-request status_code: %s' % resp.status)
                cookies = session.cookie_jar.filter_cookies(self.book_url)
                await retry_client.close()
            try:
                self.access_token = cookies['access-token'].value.replace('%20', ' ')
            except KeyError:
                log_error('Error occurred during ChitaiGorod pre-request %s' % resp.status)

    async def check_access_token(self):
        if self.access_token is None:
            await self.pre_request()
            if self.access_token is None:
                log_error('Error occurred during ChitaiGorod pre-request')
                return False
        return True

    async def get_books_json(self, search_query: str):
        if not await self.check_access_token():
            return {}

        # sleep to emulate user
        # await asyncio.sleep(1)

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
                if resp.status != HTTPStatus.OK:
                    log_error('Error occurred during ChitaiGorod request %s' % resp.status)
                    return {}
                books = await resp.json()
        return books

    async def get_books(self, search_query: str):
        book_json = await self.get_books_json(search_query)
        return self.get_parsed_books(book_json)

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
                     # image_url=f'{self.image_url}/{book["attributes"]["picture"]}?width=400&height=560&fit=bounds'
                     )
                for book in books_result if book['type'] == 'product'
            ]
        return books

    @staticmethod
    def get_authors(book):
        authors = book.get('authors')
        if not authors:
            return ''
        str_authors = [f'{a.get("firstName")} {a.get("middleName")} {a.get("lastName")}' for a in authors]
        return ', '.join(str_authors)


async def main():
    cg_store = ChitaiGorod()
    cg_books = await cg_store.get_books('мастер и маргарита')
    pprint(cg_books)


if __name__ == '__main__':
    asyncio.run(main())
