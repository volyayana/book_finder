import pytest

from dotenv import load_dotenv

load_dotenv("fixtures/test.environment", override=True)

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
