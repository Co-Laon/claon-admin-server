import asyncio

import nest_asyncio
import pytest

nest_asyncio.apply()


@pytest.fixture(scope="session")
def event_loop():
    yield asyncio.get_event_loop()
