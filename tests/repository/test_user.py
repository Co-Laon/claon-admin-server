import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.user import (
    UserRepository,
    LectorRepository,
    User,
    Lector,
    LectorApprovedFileRepository, LectorApprovedFile
)

user_repository = UserRepository()
lector_repository = LectorRepository()
lector_approved_file_repository = LectorApprovedFileRepository()


@pytest.mark.asyncio
async def test_save_lector(
        session: AsyncSession,
        user_fixture,
        lector_fixture
):
    # then
    assert lector_fixture.user.id == user_fixture.id
    assert lector_fixture.user == user_fixture
    assert lector_fixture.is_setter
    assert lector_fixture.contest[0].year == 2021
    assert lector_fixture.contest[0].title == 'title'
    assert lector_fixture.contest[0].name == 'name'
    assert lector_fixture.certificate[0].acquisition_date == '2012-10-15'
    assert lector_fixture.certificate[0].rate == 4
    assert lector_fixture.certificate[0].name == 'certificate'
    assert lector_fixture.career[0].start_date == '2016-01-01'
    assert lector_fixture.career[0].end_date == '2020-01-01'
    assert lector_fixture.career[0].name == 'career'
    assert lector_fixture.approved is False


@pytest.mark.asyncio
async def test_find_user_by_valid_id(
        session: AsyncSession,
        user_fixture,
        lector_fixture
):
    # given
    user_id = user_fixture.id

    # when
    result = await user_repository.find_by_id(session, user_id)

    # then
    assert result.id == user_fixture.id
    assert result.nickname == user_fixture.nickname
    assert result.profile_img == user_fixture.profile_img
    assert result.sns == user_fixture.sns
    assert result.email == user_fixture.email
    assert result.instagram_name == user_fixture.instagram_name
    assert result.role == user_fixture.role


@pytest.mark.asyncio
async def test_find_user_by_invalid_id(
        session: AsyncSession,
        user_fixture):
    # given
    wrong_id = "wrong_id"

    # when
    result = await user_repository.find_by_id(session, wrong_id)

    # then
    assert not result


@pytest.mark.asyncio
async def test_exist_user_by_valid_id(
        session: AsyncSession,
        user_fixture):
    # given
    user_id = user_fixture.id

    # when
    result = await user_repository.exist_by_id(session, user_id)

    # then
    assert result


@pytest.mark.asyncio
async def test_exist_user_by_invalid_id(
        session: AsyncSession,
        user_fixture):
    # given
    wrong_id = "wrong_id"

    # when
    result = await user_repository.exist_by_id(session, wrong_id)

    # then
    assert not result


@pytest.mark.asyncio
async def test_find_user_by_not_existing_nickname(
        session: AsyncSession,
        user_fixture):
    # given
    nickname = "not_existing_nickname"

    # when
    result = await user_repository.find_by_nickname(session, nickname)

    # then
    assert not result


@pytest.mark.asyncio
async def test_find_user_by_existing_nickname(
        session: AsyncSession,
        user_fixture):
    # given
    nickname = user_fixture.nickname

    # when
    result = await user_repository.find_by_nickname(session, nickname)

    # then
    assert result.id == user_fixture.id
    assert result.role == user_fixture.role
    assert result.nickname == user_fixture.nickname
    assert result.profile_img == user_fixture.profile_img
    assert result.sns == user_fixture.sns
    assert result.email == user_fixture.email
    assert result.instagram_name == user_fixture.instagram_name


@pytest.mark.asyncio
async def test_exist_user_by_not_existing_nickname(
        session: AsyncSession,
        user_fixture):
    # given
    nickname = "not_existing_nickname"

    # when
    result = await user_repository.exist_by_nickname(session, nickname)

    # then
    assert not result


@pytest.mark.asyncio
async def test_exist_user_by_existing_nickname(
        session: AsyncSession,
        user_fixture):
    # given
    nickname = user_fixture.nickname

    # when
    result = await user_repository.exist_by_nickname(session, nickname)

    # then
    assert result


@pytest.mark.asyncio
async def test_save_lector_approved_file(
        session: AsyncSession,
        lector_fixture,
        lector_approved_file_fixture: LectorApprovedFile
):
    # then
    assert lector_approved_file_fixture.lector == lector_fixture
    assert lector_approved_file_fixture.url == "https://test.com/test.pdf"


@pytest.mark.asyncio
async def test_save_all_lector_approved_files(
        session: AsyncSession,
        lector_fixture,
        lector_approved_file_fixture: LectorApprovedFile
):
    # when
    lector_approved_files = await lector_approved_file_repository.save_all(session, [lector_approved_file_fixture])

    # then
    assert lector_approved_files == [lector_approved_file_fixture]
