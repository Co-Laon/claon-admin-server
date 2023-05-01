from datetime import datetime

import pytest
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import WallType, Role, MembershipType, PeriodType
from claon_admin.schema.center import (
    CenterRepository,
    CenterApprovedFileRepository, CenterHoldRepository, CenterWallRepository, Center, CenterHold, CenterWall,
    CenterApprovedFile, CenterImage, OperatingTime, Utility, CenterFee, CenterFeeImage, CenterFeeRepository, Review,
    ReviewRepository, ReviewAnswerRepository, ReviewTag, ReviewAnswer, Post, PostRepository, ClimbingHistoryRepository,
    ClimbingHistory, PostImage
)
from claon_admin.schema.user import User, UserRepository

user_repository = UserRepository()
center_repository = CenterRepository()
center_approved_file_repository = CenterApprovedFileRepository()
center_fee_repository = CenterFeeRepository()
center_hold_repository = CenterHoldRepository()
center_wall_repository = CenterWallRepository()
review_repository = ReviewRepository()
review_answer_repository = ReviewAnswerRepository()
post_repository = PostRepository()
climbing_history_repository = ClimbingHistoryRepository()


@pytest.fixture
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
        membership_type=MembershipType.PACKAGE,
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
        is_color=False,
        img="hold_img"
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
async def climbing_history_fixture(session: AsyncSession, post_fixture: Post, center_holds_fixture: CenterHold,
                                   center_walls_fixture: CenterWall):
    history = ClimbingHistory(
        post=post_fixture,
        hold_id=center_holds_fixture.id,
        hold_url=center_holds_fixture.img,
        difficulty=center_holds_fixture.difficulty,
        challenge_count=2,
        wall_name=center_walls_fixture.name,
        wall_type=center_walls_fixture.type
    )

    history = await climbing_history_repository.save(session, history)
    yield history
    await session.rollback()


@pytest.fixture
async def review_fixture(session: AsyncSession, user_fixture: User, center_fixture: Center):
    review = Review(
        user=user_fixture,
        center=center_fixture,
        content="content",
        created_at=datetime(2023, 1, 1),
        tag=[ReviewTag(word="tag")],
        is_review=True
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


@pytest.mark.asyncio
async def test_save_center(
        session: AsyncSession,
        user_fixture: User,
        center_fixture: Center
):
    # then
    assert center_fixture.user.id == user_fixture.id
    assert center_fixture.user == user_fixture
    assert center_fixture.name == "test center"
    assert center_fixture.profile_img == "https://test.profile.png"
    assert center_fixture.address == "test_address"
    assert center_fixture.detail_address == "test_detail_address"
    assert center_fixture.tel == "010-1234-5678"
    assert center_fixture.web_url == "http://test.com"
    assert center_fixture.instagram_name == "test_instagram"
    assert center_fixture.youtube_url == "https://www.youtube.com/@test"
    assert center_fixture.center_img[0].url == "https://test.image.png"
    assert center_fixture.operating_time[0].day_of_week == "월"
    assert center_fixture.operating_time[0].start_time == "09:00"
    assert center_fixture.operating_time[0].end_time == "18:00"
    assert center_fixture.utility[0].name == "test_utility"
    assert center_fixture.fee_img[0].url == "https://test.fee.png"
    assert center_fixture.approved is False
    assert await center_repository.find_by_id(session, center_fixture.id) == center_fixture
    assert await center_repository.exists_by_id(session, center_fixture.id) is True


@pytest.mark.asyncio
async def test_find_center_by_id(
        session: AsyncSession,
        center_fixture: Center
):
    # given
    center_id = center_fixture.id

    # when
    result = await center_repository.find_by_id(session, center_id)

    # then
    assert result == center_fixture


@pytest.mark.asyncio
async def test_find_center_by_non_existing_id(
        session: AsyncSession,
):
    # given
    center_id = "non_existing_id"

    # when
    result = await center_repository.find_by_id(session, center_id)

    # then
    assert result is None


@pytest.mark.asyncio
async def test_exists_center_by_id(
        session: AsyncSession,
        center_fixture: Center
):
    # given
    center_id = center_fixture.id

    # when
    result = await center_repository.exists_by_id(session, center_id)

    # then
    assert result is True


@pytest.mark.asyncio
async def test_exists_center_by_non_existing_id(
        session: AsyncSession
):
    # given
    center_id = "non_existing_id"

    # when
    result = await center_repository.exists_by_id(session, center_id)

    # then
    assert result is False


@pytest.mark.asyncio
async def test_approve_center(
        session: AsyncSession,
        center_fixture: Center
):
    # when
    result = await center_repository.approve(session, center_fixture)

    # then
    assert result.approved is True


@pytest.mark.asyncio
async def test_delete_center(
        session: AsyncSession,
        center_fixture: Center
):
    # when
    await center_repository.delete(session, center_fixture)

    # then
    assert await center_repository.find_by_id(session, center_fixture.id) is None
    assert await center_hold_repository.find_all_by_center_id(session, center_fixture.id) == []
    assert await center_wall_repository.find_all_by_center_id(session, center_fixture.id) == []
    assert await center_fee_repository.find_all_by_center_id(session, center_fixture.id) == []
    assert await center_approved_file_repository.find_all_by_center_id(session, center_fixture.id) == []

@pytest.mark.asyncio
async def test_find_all_center_by_approved_false(
        session: AsyncSession,
        center_fixture: Center
):
    # when
    result = await center_repository.find_all_by_approved_false(session)

    # then
    assert result == [center_fixture]

@pytest.mark.asyncio
async def test_save_center_approved_file(
        session: AsyncSession,
        user_fixture: User,
        center_fixture: Center,
        center_approved_file_fixture: CenterApprovedFile
):
    # then
    assert center_approved_file_fixture.center == center_fixture
    assert center_approved_file_fixture.center_id == center_fixture.id
    assert center_approved_file_fixture.user == user_fixture
    assert center_approved_file_fixture.user_id == user_fixture.id
    assert center_approved_file_fixture.url == "https://example.com/approved.jpg"
    assert await center_approved_file_repository.find_all_by_center_id(session, center_fixture.id) == [
        center_approved_file_fixture]


@pytest.mark.asyncio
async def test_save_all_center_approved_files(
        session: AsyncSession,
        user_fixture: User,
        center_fixture: Center,
        center_approved_file_fixture: CenterApprovedFile
):
    # when
    center_approved_files = await center_approved_file_repository.save_all(session, [center_approved_file_fixture])

    # then
    assert center_approved_files == [center_approved_file_fixture]


@pytest.mark.asyncio
async def test_find_all_center_approved_files_by_center_id(
        session: AsyncSession,
        center_fixture: Center,
        center_approved_file_fixture: CenterApprovedFile
):
    # when
    center_approved_files = await center_approved_file_repository.find_all_by_center_id(session, center_fixture.id)

    # then
    assert center_approved_files == [center_approved_file_fixture]


@pytest.mark.asyncio
async def test_delete_all_center_approved_files_by_center_id(
        session: AsyncSession,
        center_fixture: Center
):
    # when
    await center_approved_file_repository.delete_all_by_center_id(session, center_fixture.id)

    # then
    assert await center_approved_file_repository.find_all_by_center_id(session, center_fixture.id) == []


@pytest.mark.asyncio
async def test_save_center_hold(
        session: AsyncSession,
        center_fixture: Center,
        center_holds_fixture: CenterHold
):
    assert center_holds_fixture.center == center_fixture
    assert center_holds_fixture.name == "hold_name"
    assert center_holds_fixture.difficulty == "hard"
    assert center_holds_fixture.is_color is False
    assert center_holds_fixture.img == "hold_img"
    assert await center_hold_repository.find_all_by_center_id(session, center_fixture.id) == [center_holds_fixture]


@pytest.mark.asyncio
async def test_save_all_center_holds(
        session: AsyncSession,
        center_fixture: Center,
        center_holds_fixture: CenterHold
):
    # when
    center_holds = await center_hold_repository.save_all(session, [center_holds_fixture])

    # then
    assert center_holds == [center_holds_fixture]


@pytest.mark.asyncio
async def test_find_all_center_holds_by_center_id(
        session: AsyncSession,
        center_fixture: Center,
        center_holds_fixture: CenterHold
):
    # when
    center_holds = await center_hold_repository.find_all_by_center_id(session, center_fixture.id)

    # then
    assert center_holds == [center_holds_fixture]


@pytest.mark.asyncio
async def test_save_center_wall(
        session: AsyncSession,
        center_fixture: Center,
        center_walls_fixture: CenterWall
):
    assert center_walls_fixture.center == center_fixture
    assert center_walls_fixture.name == "wall"
    assert center_walls_fixture.type == WallType.ENDURANCE.value
    assert await center_wall_repository.find_all_by_center_id(session, center_fixture.id) == [center_walls_fixture]


@pytest.mark.asyncio
async def test_save_all_center_walls(
        session: AsyncSession,
        center_fixture: Center,
        center_walls_fixture: CenterWall
):
    # when
    center_walls = await center_wall_repository.save_all(session, [center_walls_fixture])

    # then
    assert center_walls == [center_walls_fixture]


@pytest.mark.asyncio
async def test_find_all_center_walls_by_center_id(
        session: AsyncSession,
        center_fixture: Center,
        center_walls_fixture: CenterWall
):
    # when
    center_walls = await center_wall_repository.find_all_by_center_id(session, center_fixture.id)

    # then
    assert center_walls == [center_walls_fixture]


@pytest.mark.asyncio
async def test_save_center_fee(
        session: AsyncSession,
        center_fixture: Center,
        center_fee_fixture: CenterFee
):
    assert center_fee_fixture.center == center_fixture
    assert center_fee_fixture.name == "fee_name"
    assert center_fee_fixture.membership_type == MembershipType.PACKAGE
    assert center_fee_fixture.price == 1000
    assert center_fee_fixture.count == 2
    assert center_fee_fixture.period == 2
    assert center_fee_fixture.period_type == PeriodType.MONTH
    assert await center_fee_repository.find_all_by_center_id(session, center_fixture.id) == [center_fee_fixture]


@pytest.mark.asyncio
async def test_save_all_center_fees(
        session: AsyncSession,
        center_fixture: Center,
        center_fee_fixture: CenterFee
):
    # when
    center_fees = await center_fee_repository.save_all(session, [center_fee_fixture])

    # then
    assert center_fees == [center_fee_fixture]


@pytest.mark.asyncio
async def test_find_all_center_fees_by_center_id(
        session: AsyncSession,
        center_fixture: Center,
        center_fee_fixture: CenterFee
):
    # when
    center_fees = await center_fee_repository.find_all_by_center_id(session, center_fixture.id)

    # then
    assert center_fees == [center_fee_fixture]


@pytest.mark.asyncio
async def test_save_post(
        session: AsyncSession,
        user_fixture: User,
        post_fixture: Post
):
    assert post_fixture.user == user_fixture
    assert post_fixture.content == "content"
    assert post_fixture.img[0].url == "url"
    assert post_fixture.created_at == datetime(2023, 1, 1)


@pytest.mark.asyncio
async def test_save_review(
        session: AsyncSession,
        user_fixture: User,
        center_fixture: Center,
        review_fixture: Review
):
    assert review_fixture.user == user_fixture
    assert review_fixture.center == center_fixture
    assert review_fixture.content == "content"
    assert review_fixture.tag[0].word == "tag"
    assert review_fixture.created_at == datetime(2023, 1, 1)


@pytest.mark.asyncio
async def test_save_review_answer(
        session: AsyncSession,
        review_fixture: Review,
        review_answer_fixture: ReviewAnswer
):
    assert review_answer_fixture.review == review_fixture
    assert review_answer_fixture.content == "content"
    assert review_answer_fixture.created_at == datetime(2023, 1, 2)


@pytest.mark.asyncio
async def test_save_climbing_history(
        session: AsyncSession,
        post_fixture: Post,
        climbing_history_fixture: ClimbingHistory
):
    assert climbing_history_fixture.post == post_fixture
    assert climbing_history_fixture.hold_url == "hold_img"
    assert climbing_history_fixture.difficulty == "hard"
    assert climbing_history_fixture.challenge_count == 2
    assert climbing_history_fixture.wall_name == "wall"
    assert climbing_history_fixture.wall_type == WallType.ENDURANCE.value


@pytest.mark.asyncio
async def test_find_posts_by_center(
        session: AsyncSession,
        center_fixture: Center,
        post_fixture: Post
):
    # given
    params = Params(page=1, size=10)

    # then
    assert await post_repository.find_posts_by_center(
        session,
        params,
        center_fixture.id,
        None,
        datetime(2022, 3, 1),
        datetime(2023, 2, 28)
    ) == Page.create(items=[post_fixture], params=params, total=1)


@pytest.mark.asyncio
async def test_find_posts_by_center_not_included_hold(
        session: AsyncSession,
        center_fixture: Center,
        post_fixture: Post
):
    # given
    params = Params(page=1, size=10)

    # then
    assert await post_repository.find_posts_by_center(
        session,
        params,
        center_fixture.id,
        "not included hold id",
        datetime(2022, 3, 1),
        datetime(2023, 2, 28)
    ) == Page.create(items=[], params=params, total=0)


@pytest.mark.asyncio
async def test_find_posts_by_center_included_hold(
        session: AsyncSession,
        center_fixture: Center,
        climbing_history_fixture: ClimbingHistory,
        post_fixture: Post
):
    # given
    params = Params(page=1, size=10)

    # then
    assert await post_repository.find_posts_by_center(
        session=session,
        params=params,
        center_id=center_fixture.id,
        hold_id=climbing_history_fixture.hold_id,
        start=datetime(2022, 3, 1),
        end=datetime(2023, 2, 28)
    ) == Page.create(items=[post_fixture], params=params, total=1)
