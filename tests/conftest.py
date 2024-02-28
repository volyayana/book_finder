import pytest

from store.chitai_gorod import ChitaiGorod
from store.labirint import Labirint


@pytest.fixture
def labirint():
    return Labirint()


@pytest.fixture
def chitai_gorod():
    return ChitaiGorod()
