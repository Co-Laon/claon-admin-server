from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import Role, CenterFeeType, PeriodType, WallType
from claon_admin.schema.center import (
    CenterRepository,
    CenterApprovedFileRepository, CenterHoldRepository, CenterWallRepository, Center, CenterHold, CenterWall,
    CenterApprovedFile, CenterImage, OperatingTime, Utility, CenterFee, CenterFeeImage, CenterFeeRepository, Review,
    ReviewRepository, ReviewAnswerRepository, ReviewTag, ReviewAnswer, CenterSchedule, CenterScheduleRepository,
    CenterScheduleMemberRepository, CenterScheduleMember
)
from claon_admin.schema.post import Post, PostImage, PostRepository
from claon_admin.schema.user import User, UserRepository

user_repository = UserRepository()
center_repository = CenterRepository()
center_approved_file_repository = CenterApprovedFileRepository()
center_fee_repository = CenterFeeRepository()
center_hold_repository = CenterHoldRepository()
center_wall_repository = CenterWallRepository()
post_repository = PostRepository()
review_repository = ReviewRepository()
review_answer_repository = ReviewAnswerRepository()
center_schedule_repository = CenterScheduleRepository()
center_schedule_member_repository = CenterScheduleMemberRepository()


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
async def review_user_fixture(session: AsyncSession):
    user = User(
        oauth_id="r_oauth_id",
        nickname="r_nickname",
        profile_img="r_profile_img",
        sns="r_sns",
        email="r_test@test.com",
        instagram_name="r_instagram_name",
        role=Role.USER,
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
async def another_center_fixture(session: AsyncSession):
    center = Center(
        name="another test center",
        profile_img="https://another.test.profile.png",
        address="another_test_address",
        detail_address="another_test_detail_address",
        tel="010-1234-3333",
        web_url="http://another.test.com",
        instagram_name="another_instagram",
        youtube_url="https://www.another.youtube.com/@test",
        center_img=[CenterImage(url="https://another.test.image.png")],
        operating_time=[OperatingTime(day_of_week="월", start_time="09:00", end_time="18:00")],
        utility=[Utility(name="another_utility")],
        fee_img=[CenterFeeImage(url="https://another.test.fee.png")],
        approved=False
    )

    center = await center_repository.save(session, center)
    yield center
    await session.rollback()


@pytest.fixture
async def center_approved_file_fixture(session: AsyncSession, user_fixture: User, center_fixture: Center):
    center_approved_file = CenterApprovedFile(
        user=user_fixture,
        center=center_fixture,
        url="https://example.com/approved.jpg"
    )

    center_approved_file = await center_approved_file_repository.save(session, center_approved_file)
    yield center_approved_file
    await session.rollback()


@pytest.fixture
async def center_fee_fixture(session: AsyncSession, center_fixture: Center):
    center_fee = CenterFee(
        center=center_fixture,
        name="fee_name",
        fee_type=CenterFeeType.PACKAGE,
        price=1000,
        count=2,
        period=2,
        period_type=PeriodType.MONTH
    )

    center_fee = await center_fee_repository.save(session, center_fee)
    yield center_fee
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
async def review_fixture(session: AsyncSession, user_fixture: User, center_fixture: Center):
    review = Review(
        user=user_fixture,
        center=center_fixture,
        content="content",
        created_at=datetime(2023, 1, 1),
        tag=[ReviewTag(word="tag"), ReviewTag(word="tag2")]
    )

    review = await review_repository.save(session, review)
    yield review
    await session.rollback()


@pytest.fixture
async def other_review_fixture(session: AsyncSession, review_user_fixture: User, center_fixture: Center):
    review = Review(
        user=review_user_fixture,
        center=center_fixture,
        content="other content",
        created_at=datetime(2023, 2, 2),
        tag=[ReviewTag(word="tag3"), ReviewTag(word="tag4")]
    )

    review = await review_repository.save(session, review)
    yield review
    await session.rollback()


@pytest.fixture
async def review_answer_fixture(session: AsyncSession, review_fixture: Review):
    review_answer = ReviewAnswer(
        review=review_fixture,
        content="content",
        created_at=datetime(2023, 1, 2),
    )

    review_answer = await review_answer_repository.save(session, review_answer)
    yield review_answer
    await session.rollback()


@pytest.fixture
async def schedule_fixture(session: AsyncSession, center_fixture: Center):
    schedule = CenterSchedule(
        center=center_fixture,
        title="title",
        start_time=datetime(2023, 8, 1, 10, 0),
        end_time=datetime(2023, 8, 2, 10, 0),
        description="test"
    )

    schedule = await center_schedule_repository.save(session, schedule)
    yield schedule
    await session.rollback()


@pytest.fixture
async def schedule_member_fixture(session: AsyncSession, user_fixture: User, schedule_fixture: CenterSchedule):
    schedule_member = CenterScheduleMember(
        user=user_fixture,
        schedule=schedule_fixture,
    )

    schedule_member = await center_schedule_member_repository.save(session, schedule_member)
    yield schedule_member
    await session.rollback()
