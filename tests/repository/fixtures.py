from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.model.enum import Role, WallType
from claon_admin.schema.center import CenterRepository, Center, CenterImage, OperatingTime, Utility, CenterFee, \
    CenterFeeImage, CenterHold, CenterWall, CenterApprovedFileRepository, CenterApprovedFile
from claon_admin.schema.user import User, UserRepository, LectorRepository, Lector, Contest, Certificate, Career, \
    LectorApprovedFile, LectorApprovedFileRepository

user_repository = UserRepository()
lector_repository = LectorRepository()
lector_approved_file_repository = LectorApprovedFileRepository()
center_repository = CenterRepository()
center_approved_file_repository = CenterApprovedFileRepository()


@pytest.fixture(scope="session")
async def user_fixture(session: AsyncSession):
    user = User(
        nickname="nickname",
        profile_img="profile_img",
        sns="sns",
        email="test@test.com",
        instagram_name="instagram_name",
        role=Role.PENDING,
    )

    user = await user_repository.save(session, user)
    yield user


@pytest.fixture(scope="session")
async def lector_fixture(session: AsyncSession, user_fixture: User):
    lector = Lector(
        user=user_fixture,
        is_setter=True,
        total_experience=3,
        approved=True,
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
        ]
    )

    lector = await lector_repository.save(session, lector)
    yield lector


@pytest.fixture(scope="session")
async def center_fixture(session: AsyncSession, user_fixture: User):
    center = Center(
        user_id=user_fixture.id,
        user=user_fixture,
        name="test center",
        profile_img="https://test.profile.png",
        address="test_address",
        detail_address="test_detail_address",
        tel="010-1234-5678",
        web_url="http://test.com",
        instagram_name="test_instagram",
        youtube_url="https://www.youtube.com/@test",
        center_img=[CenterImage(url="https://test.image.png")],
        operating_time=[OperatingTime(day_of_week="월", start_time="09:00", end_time="18:00")],
        utility=[Utility(name="test_utility")],
        fee=[CenterFee(name="test_fee_name", price=1000, count=10)],
        fee_img=[CenterFeeImage(url="https://test.fee.png")],
        holds=[CenterHold(name="test_hold", difficulty="#ffffff", is_color=True)],
        walls=[CenterWall(name="test_wall", type=WallType.ENDURANCE.value)],
        approved=False
    )

    center = await center_repository.save(session, center)
    yield center


@pytest.fixture(scope="session")
async def lector_approved_file_fixture(session: AsyncSession, lector_fixture: Lector):
    lector_approved_file = LectorApprovedFile(
        lector_id=lector_fixture.id,
        lector=lector_fixture,
        url="https://test.com/test.pdf"
    )

    lector_approved_file = await lector_approved_file_repository.save(session, lector_approved_file)
    yield lector_approved_file


@pytest.fixture(scope="session")
async def center_approved_file_fixture(session: AsyncSession, user_fixture: User, center_fixture: Center):
    center_approved_file = CenterApprovedFile(
        user_id=user_fixture.id,
        user=user_fixture,
        center_id=center_fixture.id,
        center=center_fixture,
        url="https://example.com/approved.jpg"
    )

    center_approved_file = await center_approved_file_repository.save(session, center_approved_file)
    yield center_approved_file
