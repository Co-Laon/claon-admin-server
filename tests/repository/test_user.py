from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.model.enum import Role
from claon_admin.schema.user import (
    UserRepository,
    LectorRepository,
    User,
    Lector,
    Contest,
    Certificate,
    Career,
    LectorApprovedFile
)

user_repository = UserRepository()
lector_repository = LectorRepository()


@pytest.fixture(scope="session")
async def lector_fixture(session: AsyncSession, user_fixture: User):
    lector = Lector(
        user=user_fixture,
        is_setter=True,
        total_experience=3,
        contest=Contest(year=2021, title='test_title', name='test_name'),
        certificate=Certificate(acquisition_date=date.fromisoformat('2012-10-15'), rate=4, name='test_certificate'),
        career=Career(start_date=date.fromisoformat('2016-01-01'),
                      end_date=date.fromisoformat('2020-01-01'),
                      name='test_career'),
        approved=True
    )
    lector_approved_files = LectorApprovedFile(url='https://test.com/test.pdf')
    lector.approved_files.append(lector_approved_files)

    await lector_repository.save(session, lector)
    yield lector


@pytest.mark.asyncio
async def test_save(session: AsyncSession, user_fixture: User, lector_fixture: Lector):
    # then
    assert user_fixture.role == Role.LECTOR
    assert user_fixture.nickname == 'test_nick'
    assert user_fixture.profile_img == 'test_profile'
    assert user_fixture.sns == 'test_sns'
    assert user_fixture.email == 'test@test.com'
    assert user_fixture.instagram_name == 'test_insta'
    assert lector_fixture.user.id == user_fixture.id
    assert lector_fixture.is_setter
    assert lector_fixture.total_experience == 3
    assert lector_fixture.contest.year == 2021
    assert lector_fixture.contest.title == 'test_title'
    assert lector_fixture.contest.name == 'test_name'
    assert lector_fixture.certificate.acquisition_date == '2012-10-15'
    assert lector_fixture.certificate.rate == 4
    assert lector_fixture.certificate.name == 'test_certificate'
    assert lector_fixture.career.start_date == '2016-01-01'
    assert lector_fixture.career.end_date == '2020-01-01'
    assert lector_fixture.career.name == 'test_career'
    assert lector_fixture.approved
    assert lector_fixture.approved_files[0].url == 'https://test.com/test.pdf'


@pytest.mark.asyncio
async def test_find_by_valid_id(session: AsyncSession, user_fixture: User, lector_fixture: Lector):
    # given
    user_id = user_fixture.id

    # when
    result = await user_repository.find_by_id(session, user_id)

    # then
    assert result.id == user_id
    assert result.role == Role.LECTOR
    assert result.nickname == 'test_nick'
    assert result.profile_img == 'test_profile'
    assert result.sns == 'test_sns'
    assert result.email == 'test@test.com'
    assert result.instagram_name == 'test_insta'
    assert lector_fixture.user.id == result.id


@pytest.mark.asyncio
async def test_find_by_invalid_id(session: AsyncSession, user_fixture: User):
    # given
    wrong_id = "wrong_id"

    # when
    result = await user_repository.find_by_id(session, wrong_id)

    # then
    assert not result


@pytest.mark.asyncio
async def test_exist_by_valid_id(session: AsyncSession, user_fixture: User):
    # given
    user_id = user_fixture.id

    # when
    result = await user_repository.exist_by_id(session, user_id)

    # then
    assert result


@pytest.mark.asyncio
async def test_exist_by_invalid_id(session: AsyncSession, user_fixture: User):
    # given
    wrong_id = "wrong_id"

    # when
    result = await user_repository.exist_by_id(session, wrong_id)

    # then
    assert not result
