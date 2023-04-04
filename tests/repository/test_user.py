import pytest

from claon_admin.schema.user import UserRepository, User

user_repository = UserRepository()


@pytest.fixture(scope="session")
async def user_fixture(session):
    user = await user_repository.save(session, User(
        profile_image="image.claon.com/dummy.jpeg",
        nickname="dummy",
        email="dummy@claon.com",
        instagram_nickname="@dummy_instagram",
        role="dummy_role"
    ))
    yield user


@pytest.mark.asyncio
async def test_save(session, user_fixture):
    # then
    assert user_fixture.profile_image == "image.claon.com/dummy.jpeg"
    assert user_fixture.nickname == "dummy"
    assert user_fixture.email == "dummy@claon.com"
    assert user_fixture.instagram_nickname == "@dummy_instagram"
    assert user_fixture.role == "dummy_role"


@pytest.mark.asyncio
async def test_find_by_valid_id(session, user_fixture):
    # given
    user_id = user_fixture.id

    # when
    result = await user_repository.find_by_id(session, user_id)

    # then
    assert result.id == user_id
    assert result.profile_image == user_fixture.profile_image
    assert result.nickname == user_fixture.nickname
    assert result.email == user_fixture.email
    assert result.instagram_nickname == user_fixture.instagram_nickname
    assert result.role == user_fixture.role


@pytest.mark.asyncio
async def test_find_by_invalid_id(session, user_fixture):
    # given
    user_id = "wrong_id"

    # when
    result = await user_repository.find_by_id(session, user_id)

    # then
    assert result is None


@pytest.mark.asyncio
async def test_exist_by_valid_id(session, user_fixture):
    # given
    user_id = user_fixture.id

    # when
    result = await user_repository.exist_by_id(session, user_id)

    # then
    assert result is True


@pytest.mark.asyncio
async def test_exist_by_invalid_id(session, user_fixture):
    # given
    user_id = "wrong_id"

    # when
    result = await user_repository.exist_by_id(session, user_id)

    # then
    assert result is False
