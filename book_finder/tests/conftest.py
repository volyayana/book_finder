import pytest

from dotenv import load_dotenv

load_dotenv("tests/fixtures/test.environment", override=True)

import os
print(os.getenv('LIMIT_BOOKS'))

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
