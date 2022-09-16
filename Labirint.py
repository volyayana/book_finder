from bs4 import BeautifulSoup
import requests
from urllib.parse import quote

class Labirint():
    def __init__(self, search_query):
        self.url = 'https://www.labirint.ru/search'
        self.headers = {'User-agent': 'Mozilla/5.0'}
        self.params = 'available=1&paperbooks=1'
        self.books = self.get_books(search_query)

    def get_books(self, search_query):
        page = requests.get(f'{ self.url }/{ quote(search_query) }/?{self.params}',
                            headers=self.headers,)
        soup = BeautifulSoup(page.text, "html.parser")
        articles = soup.findAll(class_='product')
        books = []
        for article in articles:
            found = {}
            found['id'] = article['data-product-id']
            found['name'] = article['data-name']
            found['price'] = min(article['data-price'], article['data-discount-price'])
            books.append(found)
        return books


l = Labirint('академия азимов')
print(l.books)
