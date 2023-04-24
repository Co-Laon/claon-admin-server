import asyncio
import nest_asyncio
import pytest

nest_asyncio.apply()


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session", autouse=True)
async def db():
    from claon_admin.container import db

    asyncio.run(db.drop_database())
    asyncio.run(db.create_database())

    yield db
    await db._engine.dispose()


@pytest.fixture(scope="session")
async def session(db):
    try:
        async with db.async_session_maker() as session:
            yield session
    finally:
        await session.rollback()
        await session.close()
