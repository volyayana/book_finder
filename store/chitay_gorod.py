import asyncio

import aiohttp
from pprint import pprint

from models import Book


class ChitaiGorod:
    def __init__(self):
        self.store = 'Читай город'
        self.pre_url = 'https://www.chitai-gorod.ru'
        self.books_url = 'https://web-gate.chitai-gorod.ru/api/v2/search/product'
        self.book_url = 'https://www.chitai-gorod.ru'
        self.image_url = 'https://content.img-gorod.ru'
        self.access_token = None

    async def pre_request(self, search_query: str):
        params = {
            'phrase': search_query,
            'products[page]': 1,
            'products[per-page]': 48,
            'sortPreset': 'relevance',
            'filters[onlyAvailable]': 1,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.pre_url}/search',
                                   params=params,
                                   verify_ssl=False) as resp:
                cookies = session.cookie_jar.filter_cookies(self.pre_url)
                self.access_token = cookies['access-token'].value.replace('%20', ' ')

    async def get_books(self, search_query: str):
        # pre-request only to get cookies with token
        await self.pre_request(search_query)

        books = None
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
            async with session.get(self.books_url,
                                   headers=headers,
                                   params=params,
                                   verify_ssl=False) as resp:
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
