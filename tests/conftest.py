import asyncio
import nest_asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.model.enum import Role
from claon_admin.schema.user import User, UserRepository

nest_asyncio.apply()

user_repository = UserRepository()


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


@pytest.fixture(scope="session")
async def user_fixture(session: AsyncSession):
    user = User(
        nickname="test_nick",
        profile_img="test_profile",
        sns="test_sns",
        email="test@test.com",
        instagram_name="test_insta",
        role=Role.LECTOR,
    )

    user = await user_repository.save(session, user)
    yield user
