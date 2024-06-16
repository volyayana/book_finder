from unittest.mock import MagicMock

import pytest as pytest
from aiohttp_retry import RetryClient
from bs4 import ResultSet, BeautifulSoup
from unittest import mock

from store.labirint import Labirint
from tests.html_templates.labirint_book_list import books_template_with_author, books_template_without_author
from tests.html_templates.labirint_error import error_template
from tests.html_templates.labirint_success import successful_template


@pytest.mark.asyncio
async def test_parse_empty_books(labirint: Labirint):
    books = labirint.parse_books(error_template)
    assert books is None


@pytest.mark.asyncio
async def test_parse_books(labirint: Labirint):
    books = labirint.parse_books(successful_template)
    assert type(books) is ResultSet
    assert len(books) == 60


@pytest.mark.asyncio
async def test_get_books_with_author(labirint: Labirint):
    soup = BeautifulSoup(books_template_with_author, "html.parser")
    unparsed_books = soup.findAll(class_='product-card')

    books = labirint.get_books_list(unparsed_books)

    assert books[0].name == 'Москва - Ершалаим. Путеводитель по роману М. Булгакова "Мастер и Маргарита"'
    assert books[0].link == 'https://www.labirint.ru/books/452862/'
    assert books[0].price == 994
    assert books[0].store == 'Лабиринт'
    # assert books[0].image_url == 'https://img4.labirint.ru/rc/db09a202cff73f06c5797dcc4fc0cf41/363x561q80/books46/452862/cover.jpg?1571063157'
    assert books[0].author == 'Лесскис Георгий Александрович'


@pytest.mark.asyncio
async def test_books_template_without_author(labirint: Labirint):
    soup = BeautifulSoup(books_template_without_author, "html.parser")
    unparsed_books = soup.findAll(class_='product-card')

    books = labirint.get_books_list(unparsed_books)

    assert books[0].author is None


@pytest.mark.asyncio
async def test_get_labirint_books(labirint: Labirint):
    mocked_client = RetryClient
    mocked_client.get = MagicMock()
    mocked_client.get.return_value.__aenter__.return_value.status = 200
    mocked_client.get.return_value.__aenter__.return_value.text.return_value = successful_template

    books = await labirint.get_books('мастер и маргарита')

    assert len(books) == 60
    assert books[0].name == 'Мастер и Маргарита'
    assert books[0].link == 'https://www.labirint.ru/books/606810/'
    assert books[0].price == 5419
    assert books[0].store == 'Лабиринт'
    # assert books[0].image_url ==\
    #        'https://img4.labirint.ru/rc/3a6c6406a5d030a35e8745bee81165f7/363x561q80/books61/606810/cover.png?1575386794'
    assert books[0].author == 'Булгаков Михаил Афанасьевич'


@pytest.mark.asyncio
async def test_get_labirint_books_if_request_failed(labirint: Labirint):
    mocked_client = RetryClient
    mocked_client.get = MagicMock()
    mocked_client.get.return_value.__aenter__.return_value.status = 500

    with mock.patch('worker.send_error_message.delay'):
        books = await labirint.get_books('мастер и маргарита')

    assert books is None
