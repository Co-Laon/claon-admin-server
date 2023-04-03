from uuid import uuid4

import pytest

from claon_admin.schema.user import UserRepository, User

user_repository = UserRepository()


@pytest.fixture
async def user_fixture(session):
    user = await user_repository.save(session, User(
        id=str(uuid4()),
        email="dummy@claon.com",
        nickname="dummy",
        password="dummy"
    ))
    yield user


@pytest.mark.asyncio
async def test_save(session, user_fixture):
    # then
    assert user_fixture.email == "dummy@claon.com"
    assert user_fixture.nickname == "dummy"
    assert user_fixture.password == "dummy"


@pytest.mark.asyncio
async def test_find_by_id_when_null(session, user_fixture):
    # given
    user_id = "wrong_id"

    # when
    result = await user_repository.find_by_id(session, user_id)

    # then
    assert result is None


@pytest.mark.asyncio
async def test_find_by_id_when_exists(session, user_fixture):
    # given
    user_id = user_fixture.id

    # when
    result = await user_repository.find_by_id(session, user_id)

    # then
    assert result.id == user_id
    assert result.email == user_fixture.email
    assert result.nickname == user_fixture.nickname
    assert result.password == user_fixture.password
