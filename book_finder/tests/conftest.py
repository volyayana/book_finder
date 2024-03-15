import pytest

from dotenv import load_dotenv

load_dotenv("book_finder/tests/fixtures/test.environment", override=True)

import os
import logging
logging.error(os.getenv('LIMIT_BOOKS'))

from config.settings import Settings
from store.chitai_gorod import ChitaiGorod
from store.labirint import Labirint

settings = Settings()  # type: ignore


@pytest.fixture
def labirint():
    return Labirint(settings)


@pytest.fixture
def chitai_gorod():
    return ChitaiGorod(settings)
