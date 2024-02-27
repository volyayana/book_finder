from pprint import pprint

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import quote

from models import Book
from store.abstractStore import AbstractStore


class Labirint(AbstractStore):
    def __init__(self):
        self.url = 'https://www.labirint.ru'
        self.headers = {'User-agent': 'Mozilla/5.0'}
        self.params = 'order=relevance&available=1&id_genre=-1'
        self.store = 'Лабиринт'

    async def get_books(self, search_query: str):
        books = []
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{ self.url }/search/{ quote(search_query) }/',
                                   headers=self.headers,
                                   params=self.params,
                                   verify_ssl=False) as resp:
                response_text = await resp.text()
                soup = BeautifulSoup(response_text, "html.parser")
                not_found = soup.findAll(class_='search-error')
                if not_found:
                    return []
                articles = soup.findAll(class_='product-card')

                for article in articles:
                    book = Book(name=article['data-name'],
                                link=f'{self.url}{article.find(class_="product-card__img")["href"]}',
                                price=float(article['data-discount-price'] or article['data-price']),
                                store=self.store,
                                image_url=article.find('img')['data-src']
                                )
                    author = article.find(class_='product-card__author')
                    if author:
                        book.author = author.a['title']
                    books.append(book)
        return books


async def main():
    lab_store = Labirint()
    lab_books = await lab_store.get_books('мастер и маргарита')
    pprint(lab_books)


if __name__ == '__main__':
    asyncio.run(main())
