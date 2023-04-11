import asyncio
from datetime import date

import nest_asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.model.enum import Role, WallType
from claon_admin.schema.center import CenterRepository, Center, CenterImage, OperatingTime, Utility, CenterFee, \
    CenterFeeImage, CenterHold, CenterWall, CenterApprovedFile
from claon_admin.schema.user import UserRepository, LectorRepository, User, Lector, Contest, Certificate, Career, \
    LectorApprovedFile

nest_asyncio.apply()

user_repository = UserRepository()
lector_repository = LectorRepository()
center_repository = CenterRepository()

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
        nickname='nickname',
        profile_img='profile_img',
        sns='sns',
        email='test@test.com',
        instagram_name='instagram_name',
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
        approved=True
    )

    lector.contest = [
        Contest(
            year=2021,
            title='title',
            name='name'
        )
    ]

    lector.certificate = [
        Certificate(
            acquisition_date=date.fromisoformat('2012-10-15'),
            rate=4,
            name='certificate'
        )
    ]

    lector.career = [
        Career(
            start_date=date.fromisoformat('2016-01-01'),
            end_date=date.fromisoformat('2020-01-01'),
            name='career'
        )
    ]

    lector.approved_files = [LectorApprovedFile(url='https://test.com/test.pdf')]

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
