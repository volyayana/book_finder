from bs4 import BeautifulSoup
import requests
from urllib.parse import quote

class Labirint():
    def __init__(self, search_query):
        self.url = 'https://www.labirint.ru'
        self.headers = {'User-agent': 'Mozilla/5.0'}
        self.params = 'available=1&paperbooks=1'
        self.books = self.get_books(search_query)

    def get_books(self, search_query):
        page = requests.get(f'{ self.url }/search/{ quote(search_query) }/?{self.params}',
                            headers=self.headers,)
        soup = BeautifulSoup(page.text, "html.parser")
        not_found = soup.findAll(class_='search-error')
        books = []
        if not_found:
            return []
        articles = soup.findAll(class_='product')
        for article in articles:
            book_dict = {
                'link': f'{self.url}{article.find(class_="cover")["href"]}',
                'name': article['data-name'],
                'store': 'Лабиринт',
                'price': float(article['data-discount-price'] or article['data-price']),
                'image_url': article.find('img')['data-src']
            }
            try:
                book_dict['author'] = article.find(class_='product-author').a['title']
            except (AttributeError, KeyError):
                book_dict['author'] = '-'
            books.append(book_dict)
        return books


if __name__ == '__main__':
    l = Labirint('толстой детство')
    print(l.books)
