from unittest.mock import MagicMock, patch, Mock

import pytest as pytest

from aiohttp_retry import RetryClient

from store.chitai_gorod import ChitaiGorod


@pytest.mark.asyncio
async def test_get_authors_success(chitai_gorod: ChitaiGorod):
    books = {
        "authors": [
            {
                "firstName": "Test_name",
                "middleName": "Test_middle_name",
                "lastName": "Test_last_name",
            }
        ]
    }
    authors = chitai_gorod.get_authors(books)
    assert authors == "Test_name Test_middle_name Test_last_name"

@pytest.mark.asyncio
async def test_get_authors_multiple_success(chitai_gorod: ChitaiGorod):
    books = {
        "authors": [
            {
                "firstName": "Test_name",
                "middleName": "Test_middle_name",
                "lastName": "Test_last_name",
            },
            {
                "firstName": "Test_name2",
                "middleName": "Test_middle_name2",
                "lastName": "Test_last_name2",
            }
        ]
    }
    authors = chitai_gorod.get_authors(books)
    assert authors == "Test_name Test_middle_name Test_last_name, Test_name2 Test_middle_name2 Test_last_name2"

@pytest.mark.asyncio
async def test_get_authors_no_authors(chitai_gorod: ChitaiGorod):
    books = {
        "authors": []
    }
    authors = chitai_gorod.get_authors(books)
    assert authors == ""

@pytest.mark.asyncio
async def test_get_parsed_books_success(chitai_gorod: ChitaiGorod):
    book_json = {
        "included": [
            {
                "type": "product",
                "attributes": {
                    "authors": [
                        {
                            "firstName": "Test_name",
                            "middleName": "Test_middle_name",
                            "lastName": "Test_last_name",
                        }
                    ],
                    "title": "Test_title",
                    "url": "Test_url",
                    "price": 100
                }
            },
            {
                "type": "wrong_product",
                "attributes": {
                    "authors": [
                        {
                            "firstName": "Test_name2",
                            "middleName": "Test_middle_name2",
                            "lastName": "Test_last_name2",
                        }
                    ],
                    "title": "Test_title2",
                    "url": "Test_url2",
                    "price": 200
                }
            }
        ]
    }
    books = chitai_gorod.get_parsed_books(book_json)
    assert books[0].name == "Test_title"
    assert books[0].link == "https://www.chitai-gorod.ru/Test_url"
    assert books[0].price == 100
    assert books[0].store == "Читай город"
    assert books[0].author == "Test_name Test_middle_name Test_last_name"

@pytest.mark.asyncio
async def test_get_parsed_books_no_books(chitai_gorod: ChitaiGorod):
    book_json = {
        "included": []
    }
    books = chitai_gorod.get_parsed_books(book_json)
    assert books == []

@pytest.mark.asyncio
async def test_get_parsed_books_multiple_books(chitai_gorod: ChitaiGorod):
    book_json = {
        "included": [
            {
                "type": "product",
                "attributes": {
                    "authors": [
                        {
                            "firstName": "Test_name",
                            "middleName": "Test_middle_name",
                            "lastName": "Test_last_name",
                        }
                    ],
                    "title": "Test_title",
                    "url": "Test_url",
                    "price": 100
                }
            },
            {
                "type": "product",
                "attributes": {
                    "authors": [
                        {
                            "firstName": "Test_name2",
                            "middleName": "Test_middle_name2",
                            "lastName": "Test_last_name2",
                        }
                    ],
                    "title": "Test_title2",
                    "url": "Test_url2",
                    "price": 200
                }
            }
        ]
    }
    books = chitai_gorod.get_parsed_books(book_json)
    assert books[0].name == "Test_title"
    assert books[0].link == "https://www.chitai-gorod.ru/Test_url"
    assert books[0].price == 100
    assert books[0].store == "Читай город"
    assert books[0].author == "Test_name Test_middle_name Test_last_name"

    assert books[1].name == "Test_title2"
    assert books[1].link == "https://www.chitai-gorod.ru/Test_url2"
    assert books[1].price == 200
    assert books[1].store == "Читай город"
    assert books[1].author == "Test_name2 Test_middle_name2 Test_last_name2"

@pytest.mark.asyncio
@patch("aiohttp.CookieJar.filter_cookies")
async def test_pre_request_success(mock_cookies, chitai_gorod: ChitaiGorod):
    chitai_gorod.access_token = None

    mocked_client = RetryClient
    mocked_client.get = MagicMock()
    mocked_client.get.return_value.__aenter__.return_value.status = 200
    mocked_client.get.return_value.__aenter__.return_value.text.return_value = None

    mock_cookies.return_value = {
        "access-token": Mock(value="test_token"),
    }

    await chitai_gorod.pre_request()
    assert chitai_gorod.access_token == "test_token"


@pytest.mark.asyncio
@patch("aiohttp.CookieJar.filter_cookies")
async def test_pre_request_no_cookies(mock_cookies, chitai_gorod: ChitaiGorod):
    chitai_gorod.access_token = None

    mocked_client = RetryClient
    mocked_client.get = MagicMock()
    mocked_client.get.return_value.__aenter__.return_value.status = 200
    mocked_client.get.return_value.__aenter__.return_value.text.return_value = None

    mock_cookies.return_value = {}

    await chitai_gorod.pre_request()
    assert chitai_gorod.access_token is None


@pytest.mark.asyncio
async def test_pre_request_failed(chitai_gorod: ChitaiGorod):
    chitai_gorod.access_token = None

    mocked_client = RetryClient
    mocked_client.get = MagicMock()
    mocked_client.get.return_value.__aenter__.return_value.status = 500
    mocked_client.get.return_value.__aenter__.return_value.text.return_value = None

    await chitai_gorod.pre_request()
    assert chitai_gorod.access_token is None


@pytest.mark.asyncio
@patch("store.chitai_gorod.ChitaiGorod.pre_request")
async def test_check_access_token_success(mock_pre_request, chitai_gorod: ChitaiGorod):
    chitai_gorod.access_token = "test_token"
    mock_pre_request.return_value = None

    assert await chitai_gorod.check_access_token() is True

@pytest.mark.asyncio
@patch("aiohttp.CookieJar.filter_cookies")
async def test_check_access_token_new_token_success(mock_cookies, chitai_gorod: ChitaiGorod):
    chitai_gorod.access_token = None

    mocked_client = RetryClient
    mocked_client.get = MagicMock()
    mocked_client.get.return_value.__aenter__.return_value.status = 200
    mocked_client.get.return_value.__aenter__.return_value.text.return_value = None

    mock_cookies.return_value = {
        "access-token": Mock(value="test_token"),
    }

    assert await chitai_gorod.check_access_token() is True


@pytest.mark.asyncio
@patch("store.chitai_gorod.ChitaiGorod.pre_request")
async def test_check_access_token_unsuccess(mock_pre_request, chitai_gorod: ChitaiGorod):
    mock_pre_request.return_value = None

    assert await chitai_gorod.check_access_token() is False


@pytest.mark.asyncio
async def test_get_books_json_success(chitai_gorod: ChitaiGorod):
    chitai_gorod.access_token = "test_token"

    mocked_client = RetryClient
    mocked_client.get = MagicMock()
    mocked_client.get.return_value.__aenter__.return_value.status = 200
    mocked_client.get.return_value.__aenter__.return_value.json.return_value = {"books": ["test_books"]}

    books_json = await chitai_gorod.get_books_json("test_query")
    assert books_json == {"books": ["test_books"]}

@pytest.mark.asyncio
async def test_get_books_json_failed(chitai_gorod: ChitaiGorod):
    chitai_gorod.access_token = "test_token"

    mocked_client = RetryClient
    mocked_client.get = MagicMock()
    mocked_client.get.return_value.__aenter__.return_value.status = 500

    books_json = await chitai_gorod.get_books_json("test_query")
    assert books_json == {}


@pytest.mark.asyncio
@patch('store.chitai_gorod.ChitaiGorod.check_access_token')
async def test_get_books_json_no_token(mock_access_token, chitai_gorod: ChitaiGorod):
    mock_access_token.return_value = False

    assert await chitai_gorod.get_books_json("test_query") == {}
