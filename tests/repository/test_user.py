from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.model.enum import Role
from claon_admin.schema.user import (
    UserRepository,
    LectorRepository,
    User,
    LectorApprovedFileRepository, LectorApprovedFile, Lector, Career, Contest, Certificate
)

user_repository = UserRepository()
lector_repository = LectorRepository()
lector_approved_file_repository = LectorApprovedFileRepository()


@pytest.fixture(autouse=True)
async def user_fixture(session: AsyncSession):
    user = User(
        oauth_id="oauth_id",
        nickname="nickname",
        profile_img="profile_img",
        sns="sns",
        email="test@test.com",
        instagram_name="instagram_name",
        role=Role.PENDING,
    )

    user = await user_repository.save(session, user)
    yield user
    await session.rollback()


@pytest.fixture(autouse=True)
async def lector_fixture(session: AsyncSession, user_fixture: User):
    lector = Lector(
        is_setter=True,
        approved=False,
        contest=[Contest(year=2021, title="title", name="name")],
        certificate=[
            Certificate(
                acquisition_date=date.fromisoformat("2012-10-15"),
                rate=4,
                name="certificate"
            )
        ],
        career=[
            Career(
                start_date=date.fromisoformat("2016-01-01"),
                end_date=date.fromisoformat("2020-01-01"),
                name="career"
            )
        ],
        user=user_fixture
    )

    lector = await lector_repository.save(session, lector)
    yield lector
    await session.rollback()


@pytest.fixture(autouse=True)
async def lector_approved_file_fixture(session: AsyncSession, lector_fixture: Lector):
    lector_approved_file = LectorApprovedFile(
        lector=lector_fixture,
        url="https://test.com/test.pdf"
    )

    lector_approved_file = await lector_approved_file_repository.save(session, lector_approved_file)
    yield lector_approved_file
    await session.rollback()


@pytest.mark.asyncio
async def test_save_lector(
        session: AsyncSession,
        user_fixture: User,
        lector_fixture: Lector
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
async def test_delete_lector(
        session: AsyncSession,
        lector_fixture: Lector,
        lector_approved_file_fixture: LectorApprovedFile
):
    # when
    await lector_repository.delete(session, lector_fixture)

    # then
    assert await lector_repository.find_by_id(session, lector_fixture.id) is None
    assert await lector_approved_file_repository.find_all_by_lector_id(session, lector_fixture.id) == []


@pytest.mark.asyncio
async def test_find_lector_by_id(
        session: AsyncSession,
        lector_fixture: Lector
):
    # given
    lector_id = lector_fixture.id

    # when
    result = await lector_repository.find_by_id(session, lector_id)

    # then
    assert result == lector_fixture


@pytest.mark.asyncio
async def test_find_lector_by_non_existing_id(
        session: AsyncSession
):
    # given
    lector_id = "non_existing_id"

    # when
    result = await lector_repository.find_by_id(session, lector_id)

    # then
    assert result is None


@pytest.mark.asyncio
async def test_exists_lector_by_id(
        session: AsyncSession,
        lector_fixture: Lector
):
    # given
    lector_id = lector_fixture.id

    # when
    result = await lector_repository.exists_by_id(session, lector_id)

    # then
    assert result


@pytest.mark.asyncio
async def test_exists_lector_by_non_existing_id(
        session: AsyncSession
):
    # given
    lector_id = "non_existing_id"

    # when
    result = await lector_repository.exists_by_id(session, lector_id)

    # then
    assert result is False


@pytest.mark.asyncio
async def test_approve_lector(
        session: AsyncSession,
        lector_fixture: Lector
):
    # when
    result = await lector_repository.approve(session, lector_fixture)

    # then
    assert result.approved


@pytest.mark.asyncio
async def test_find_user_by_valid_id(
        session: AsyncSession,
        user_fixture: User,
        lector_fixture: Lector
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
        user_fixture: User
):
    # given
    wrong_id = "wrong_id"

    # when
    result = await user_repository.find_by_id(session, wrong_id)

    # then
    assert not result


@pytest.mark.asyncio
async def test_exist_user_by_valid_id(
        session: AsyncSession,
        user_fixture: User
):
    # given
    user_id = user_fixture.id

    # when
    result = await user_repository.exist_by_id(session, user_id)

    # then
    assert result


@pytest.mark.asyncio
async def test_exist_user_by_invalid_id(
        session: AsyncSession,
        user_fixture: User
):
    # given
    wrong_id = "wrong_id"

    # when
    result = await user_repository.exist_by_id(session, wrong_id)

    # then
    assert not result


@pytest.mark.asyncio
async def test_find_user_by_not_existing_nickname(
        session: AsyncSession,
        user_fixture: User
):
    # given
    nickname = "not_existing_nickname"

    # when
    result = await user_repository.find_by_nickname(session, nickname)

    # then
    assert not result


@pytest.mark.asyncio
async def test_find_user_by_existing_nickname(
        session: AsyncSession,
        user_fixture: User
):
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
        user_fixture: User
):
    # given
    nickname = "not_existing_nickname"

    # when
    result = await user_repository.exist_by_nickname(session, nickname)

    # then
    assert not result


@pytest.mark.asyncio
async def test_exist_user_by_existing_nickname(
        session: AsyncSession,
        user_fixture: User
):
    # given
    nickname = user_fixture.nickname

    # when
    result = await user_repository.exist_by_nickname(session, nickname)

    # then
    assert result


@pytest.mark.asyncio
async def test_save_lector_approved_file(
        session: AsyncSession,
        lector_fixture: Lector,
        lector_approved_file_fixture: LectorApprovedFile
):
    # then
    assert lector_approved_file_fixture.lector == lector_fixture
    assert lector_approved_file_fixture.url == "https://test.com/test.pdf"


@pytest.mark.asyncio
async def test_save_all_lector_approved_files(
        session: AsyncSession,
        lector_fixture: Lector,
        lector_approved_file_fixture: LectorApprovedFile
):
    # when
    lector_approved_files = await lector_approved_file_repository.save_all(session, [lector_approved_file_fixture])

    # then
    assert lector_approved_files == [lector_approved_file_fixture]


@pytest.mark.asyncio
async def test_find_all_lector_approved_files_by_lector_id(
        session: AsyncSession,
        lector_fixture: Lector,
        lector_approved_file_fixture: LectorApprovedFile
):
    # when
    lector_approved_files = await lector_approved_file_repository.find_all_by_lector_id(session, lector_fixture.id)

    # then
    assert lector_approved_files == [lector_approved_file_fixture]


@pytest.mark.asyncio
async def test_delete_all_lector_approved_files_by_lector_id(
        session: AsyncSession,
        lector_fixture: Lector
):
    # when
    lector_approved_files = await lector_approved_file_repository.delete_all_by_lector_id(session, lector_fixture.id)

    # then
    assert lector_approved_files is None


async def test_find_by_oauth_id_and_sns(session: AsyncSession, user_fixture: User):
    # given
    user_oauth_id = user_fixture.oauth_id
    user_sns = user_fixture.sns

    # when
    result = await user_repository.find_by_oauth_id_and_sns(session, user_oauth_id, user_sns)

    # then
    assert result.oauth_id == user_fixture.oauth_id
    assert result.nickname == user_fixture.nickname
    assert result.profile_img == user_fixture.profile_img
    assert result.sns == user_fixture.sns
    assert result.email == user_fixture.email
    assert result.instagram_name == user_fixture.instagram_name
    assert result.role == user_fixture.role


@pytest.mark.asyncio
async def test_find_by_invalid_oauth_id_and_sns(session: AsyncSession, user_fixture: User):
    # given
    user_oauth_id = "wrong_id"
    user_sns = user_fixture.sns

    # when
    result = await user_repository.find_by_oauth_id_and_sns(session, user_oauth_id, user_sns)

    # then
    assert not result


async def test_find_by_oauth_id(session: AsyncSession, user_fixture: User):
    # given
    user_oauth_id = user_fixture.oauth_id

    # when
    result = await user_repository.find_by_oauth_id(session, user_oauth_id)

    # then
    assert result.oauth_id == user_fixture.oauth_id
    assert result.nickname == user_fixture.nickname
    assert result.profile_img == user_fixture.profile_img
    assert result.sns == user_fixture.sns
    assert result.email == user_fixture.email
    assert result.instagram_name == user_fixture.instagram_name
    assert result.role == user_fixture.role


@pytest.mark.asyncio
async def test_find_by_invalid_oauth_id(session: AsyncSession, user_fixture: User):
    # given
    user_oauth_id = "wrong_id"

    # when
    result = await user_repository.find_by_oauth_id(session, user_oauth_id)

    # then
    assert not result


@pytest.mark.asyncio
async def test_update_role(session: AsyncSession, user_fixture: User):
    # given
    role = Role.LECTOR

    # when
    result = await user_repository.update_role(session, user_fixture, Role.LECTOR)

    # then
    assert result.role == role
