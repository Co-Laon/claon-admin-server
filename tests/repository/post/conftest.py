from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import Role, WallType
from claon_admin.common.util.time import now
from claon_admin.schema.center import Center, CenterWall, CenterHold, CenterImage, OperatingTime, Utility, \
    CenterFeeImage, CenterRepository, CenterHoldRepository, CenterWallRepository
from claon_admin.schema.post import Post, PostImage, ClimbingHistory, PostRepository, ClimbingHistoryRepository, \
    PostCountHistoryRepository, PostCountHistory
from claon_admin.schema.user import User, UserRepository

user_repository = UserRepository()
center_repository = CenterRepository()
center_hold_repository = CenterHoldRepository()
center_wall_repository = CenterWallRepository()
post_repository = PostRepository()
post_count_history_repository = PostCountHistoryRepository()
climbing_history_repository = ClimbingHistoryRepository()


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


@pytest.fixture
async def center_fixture(session: AsyncSession, user_fixture: User):
    center = Center(
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
        fee_img=[CenterFeeImage(url="https://test.fee.png")],
        approved=True
    )

    center = await center_repository.save(session, center)
    yield center
    await session.rollback()


@pytest.fixture
async def center_holds_fixture(session: AsyncSession, center_fixture: Center):
    center_hold = CenterHold(
        center=center_fixture,
        name="hold_name",
        difficulty="hard",
        is_color=False
    )

    center_hold = await center_hold_repository.save(session, center_hold)
    yield center_hold
    await session.rollback()


@pytest.fixture
async def center_walls_fixture(session: AsyncSession, center_fixture: Center):
    center_wall = CenterWall(
        center=center_fixture,
        name="wall",
        type=WallType.ENDURANCE.value
    )

    center_wall = await center_wall_repository.save(session, center_wall)
    yield center_wall
    await session.rollback()


@pytest.fixture
async def post_fixture(session: AsyncSession, user_fixture: User, center_fixture: Center):
    post = Post(
        user=user_fixture,
        center=center_fixture,
        content="content",
        created_at=datetime(2023, 1, 1),
        img=[PostImage(url="url")]
    )

    post = await post_repository.save(session, post)
    yield post
    await session.rollback()


@pytest.fixture
async def post_count_history_fixture(session: AsyncSession, center_fixture: Center):
    post_history = PostCountHistory(
        center_id=center_fixture.id,
        count=10,
        reg_date=now().date()
    )

    post_history = await post_count_history_repository.save(session, post_history)
    yield post_history
    await session.rollback()


@pytest.fixture
async def post_count_history_list_fixture(session: AsyncSession, center_fixture: Center):
    post_count_history_list = [
        PostCountHistory(
            center_id=center_fixture.id,
            count=10,
            reg_date=now().date() - timedelta(weeks=52)
        ),
        PostCountHistory(
            center_id=center_fixture.id,
            count=10,
            reg_date=now().date() - timedelta(weeks=4)
        ),
        PostCountHistory(
            center_id=center_fixture.id,
            count=10,
            reg_date=now().date() - timedelta(weeks=1)
        )
    ]

    post_count_history_list = [await post_count_history_repository.save(session, post_count_history)
                               for post_count_history in post_count_history_list]
    yield post_count_history_list
    await session.rollback()


@pytest.fixture
async def climbing_history_fixture(session: AsyncSession, post_fixture: Post, center_holds_fixture: CenterHold,
                                   center_walls_fixture: CenterWall):
    history = ClimbingHistory(
        post=post_fixture,
        hold_id=center_holds_fixture.id,
        difficulty=center_holds_fixture.difficulty,
        challenge_count=2,
        wall_name=center_walls_fixture.name,
        wall_type=center_walls_fixture.type
    )

    history = await climbing_history_repository.save(session, history)
    yield history
    await session.rollback()
