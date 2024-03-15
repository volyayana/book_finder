import pytest

from dotenv import load_dotenv

from config.settings import Settings
from store.chitai_gorod import ChitaiGorod
from store.labirint import Labirint

load_dotenv("tests/fixtures/test.environment", override=True)

settings = Settings()  # type: ignore


@pytest.fixture
def labirint():
    return Labirint(settings)


@pytest.fixture
def chitai_gorod():
    return ChitaiGorod(settings)
