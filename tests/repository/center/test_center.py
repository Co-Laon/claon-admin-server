from datetime import datetime

import pytest
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import WallType, MembershipType, PeriodType
from claon_admin.schema.center import (
    Center, CenterHold, CenterWall, CenterApprovedFile, CenterFee, Review, ReviewAnswer, Post, ClimbingHistory
)
from claon_admin.schema.user import User
from tests.repository.center.conftest import center_repository, center_hold_repository, center_wall_repository, \
    center_fee_repository, center_approved_file_repository, post_repository, review_repository, review_answer_repository


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
    assert center_fixture.approved is True


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
async def test_exists_center_by_name_and_approved(
        session: AsyncSession,
        center_fixture: Center
):
    # given
    center_name = center_fixture.name

    # when
    result = await center_repository.exists_by_name_and_approved(session, center_name)

    # then
    assert result is True


@pytest.mark.asyncio
async def test_exists_center_by_non_existing_name_and_approved(
        session: AsyncSession
):
    # given
    center_name = "non_existing_name"

    # when
    result = await center_repository.exists_by_id(session, center_name)

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
    # given
    center_fixture.approved = False

    # when
    result = await center_repository.find_all_by_approved_false(session)

    # then
    assert result == [center_fixture]


@pytest.mark.asyncio
async def test_find_centers_by_name(
    session: AsyncSession,
    center_fixture: Center,
    mock_another_center: Center
):
    # when
    result = await center_repository.find_by_name(session, center_fixture.name)

    # then
    assert result == [mock_another_center]


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


@pytest.mark.asyncio
async def test_find_posts_summary_by_center(
        session: AsyncSession,
        center_fixture: Center,
        post_fixture: Post
):
    # then
    assert await post_repository.find_posts_summary_by_center(
        session, center_fixture.id
    ) == {
        "today": 0,
        "week": 0,
        "month": 0,
        "total": 1,
        "per_day": [],
        "per_week": [(post_fixture.id, post_fixture.created_at)]
    }


@pytest.mark.asyncio
async def test_find_reviews_by_center_not_filter(
        session: AsyncSession,
        center_fixture: Center,
        review_fixture: Review,
        post_fixture: Post,
        review_answer_fixture: ReviewAnswer
):
    # given
    params = Params(page=1, size=10)

    # then
    assert await review_repository.find_reviews_by_center(
        session=session,
        params=params,
        center_id=center_fixture.id,
        start=datetime(2022, 3, 1),
        end=datetime(2023, 2, 28),
        tag=None,
        is_answered=None
    ) == Page.create(items=[(review_fixture, 1)], params=params, total=1)


@pytest.mark.asyncio
async def test_find_reviews_by_center_with_tag(
        session: AsyncSession,
        center_fixture: Center,
        review_fixture: Review,
        post_fixture: Post,
        review_answer_fixture: ReviewAnswer
):
    # given
    params = Params(page=1, size=10)

    # then
    assert await review_repository.find_reviews_by_center(
        session=session,
        params=params,
        center_id=center_fixture.id,
        start=datetime(2022, 3, 1),
        end=datetime(2023, 2, 28),
        tag="tag",
        is_answered=None
    ) == Page.create(items=[(review_fixture, 1)], params=params, total=1)


@pytest.mark.asyncio
async def test_find_reviews_with_by_center_only_not_answered(
        session: AsyncSession,
        center_fixture: Center,
        review_fixture: Review,
        post_fixture: Post,
        review_answer_fixture: ReviewAnswer
):
    # given
    params = Params(page=1, size=10)

    # then
    assert await review_repository.find_reviews_by_center(
        session=session,
        params=params,
        center_id=center_fixture.id,
        start=datetime(2022, 3, 1),
        end=datetime(2023, 2, 28),
        tag=None,
        is_answered=False
    ) == Page.create(items=[], params=params, total=0)


@pytest.mark.asyncio
async def test_update_review_answer(
        session: AsyncSession,
        review_answer_fixture: ReviewAnswer
):
    # when
    updated_answer = await review_answer_repository.update(
        session=session,
        answer=review_answer_fixture,
        content="updated answer"
    )

    # then
    assert review_answer_fixture.content == updated_answer.content


@pytest.mark.asyncio
async def test_delete_review_answer(
        session: AsyncSession,
        review_fixture: Review,
        review_answer_fixture: ReviewAnswer
):
    # when
    await review_answer_repository.delete(
        session=session,
        answer=review_answer_fixture
    )

    # then
    assert await review_answer_repository.find_by_review_id(session, review_fixture.id) is None


@pytest.mark.asyncio
async def test_find_review_by_id_and_center_id(
        session: AsyncSession,
        center_fixture: Center,
        review_fixture: Review
):
    # then
    assert await review_repository.find_by_id_and_center_id(session, review_fixture.id, center_fixture.id) == review_fixture
