import requests
from urllib.parse import quote
from pprint import pprint


class ChitaiGorod():
    def __init__(self, search_query):
        self.goods_url = 'https://search-v2.chitai-gorod.ru/api/v3/search/'
        self.books_url = 'https://webapi.chitai-gorod.ru/web/goods/extension/list/'
        self.book_url = 'https://www.chitai-gorod.ru'
        self.image_url = 'https://img-gorod.ru'
        self.cheepest_book = None
        self.books = self.get_books(search_query)

    def get_ids(self, search_query):
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        data = f'index=goods&query={ quote(search_query) }&type=common&from=0per_page=100&filters[available]=true'
        goods = requests.post(self.goods_url,
                              headers=headers,
                              data=data).json()['ids']
        return goods

    def get_books(self, search_query):
        book_ids = self.get_ids(search_query)
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        data = 'token=123&action=read&'
        for id in book_ids:
            data += f'data[]={ id }&'
        #print(data)
        books = requests.post(self.books_url,
                              headers=headers,
                              data=data).json()
        books = self.get_sorted_books(books)
        return books

    def get_sorted_books(self, book_json):
        books = []
        if book_json.get('result'):
            for book_id, book in book_json.get('result').items():
                books.append({'author': book['author'],
                              'name': book['name'],
                              'link': f'{self.book_url}/{book["link"]}',
                              'price': book['price'],
                              'description': book['short_text'],
                              'image_url': f'{self.image_url}/{book["image_url"]}'})
            sorted(books, key=lambda x: x['price'])
            self.cheepest_book = books[0]
        return books


if __name__ == '__main__':
    cg = ChitaiGorod('три любви кронин')
    pprint(cg.books)
    pprint(cg.cheepest_book)

