from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import Role
from claon_admin.schema.user import User, UserRepository, LectorRepository, LectorApprovedFileRepository, Lector, \
    Contest, Certificate, Career, LectorApprovedFile

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
