import uuid
from datetime import datetime
from typing import List
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import UploadFile
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import WallType, Role, CenterUploadPurpose
from claon_admin.common.error.exception import BadRequestException, UnauthorizedException, ErrorCode, NotFoundException
from claon_admin.common.util.pagination import PaginationFactory, Pagination
from claon_admin.common.util.time import get_relative_time
from claon_admin.model.file import UploadFileResponseDto
from claon_admin.model.post import PostBriefResponseDto
from claon_admin.model.review import ReviewBriefResponseDto, ReviewAnswerRequestDto, ReviewAnswerResponseDto
from claon_admin.model.center import CenterNameResponseDto
from claon_admin.schema.center import CenterRepository, Center, CenterImage, OperatingTime, Utility, CenterFeeImage, \
    Post, PostImage, ClimbingHistory, PostRepository, CenterHold, CenterWall, ReviewRepository, Review, ReviewTag, \
    ReviewAnswer, ReviewAnswerRepository
from claon_admin.schema.user import User
from claon_admin.service.center import CenterService


@pytest.fixture
def mock_repo():
    center_repository = AsyncMock(spec=CenterRepository)
    post_repository = AsyncMock(spec=PostRepository)
    review_repository = AsyncMock(spec=ReviewRepository)
    review_answer_repository = AsyncMock(spec=ReviewAnswerRepository)
    pagination_factory = AsyncMock(spec=PaginationFactory)

    return {
        "center": center_repository,
        "post": post_repository,
        "review": review_repository,
        "review_answer": review_answer_repository,
        "pagination_factory": pagination_factory
    }


@pytest.fixture
def center_service(mock_repo: dict):
    return CenterService(
        mock_repo["center"],
        mock_repo["post"],
        mock_repo["review"],
        mock_repo["review_answer"],
        mock_repo["pagination_factory"]
    )


@pytest.fixture
def mock_user():
    yield User(
        id=str(uuid.uuid4()),
        oauth_id="oauth_id",
        nickname="nickname",
        profile_img="profile_img",
        sns="sns",
        email="test@test.com",
        instagram_name="instagram_name",
        role=Role.CENTER_ADMIN
    )


@pytest.fixture
def mock_pending_user():
    yield User(
        id=str(uuid.uuid4()),
        oauth_id="pending_oauth_id",
        nickname="pending_nickname",
        profile_img="pending_profile_img",
        sns="pending_sns",
        email="pending_test@test.com",
        instagram_name="pending_instagram_name",
        role=Role.PENDING
    )


@pytest.fixture
def mock_review_user():
    yield User(
        id=str(uuid.uuid4()),
        oauth_id="r_oauth_id",
        nickname="r_nickname",
        profile_img="r_profile_img",
        sns="r_sns",
        email="r_test@test.com",
        instagram_name="r_instagram_name",
        role=Role.USER
    )


@pytest.fixture
def mock_center(mock_user: User):
    yield Center(
        id=str(uuid.uuid4()),
        user=mock_user,
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


@pytest.fixture
def mock_another_center(mock_pending_user: User):
    yield Center(
        id=str(uuid.uuid4()),
        user=mock_pending_user,
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


@pytest.fixture
def mock_center_holds(mock_center: Center):
    yield [
        CenterHold(
            id=str(uuid.uuid4()),
            center=mock_center,
            name="hold",
            difficulty="hard",
            is_color=False,
            img="hold_url"
        )
    ]


@pytest.fixture
async def mock_center_walls(session: AsyncSession, mock_center: Center):
    yield [
        CenterWall(
            id=str(uuid.uuid4()),
            center=mock_center,
            name="wall",
            type=WallType.ENDURANCE.value
        )
    ]


@pytest.fixture
def mock_post(mock_user: User, mock_center: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=mock_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 3),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def mock_other_post(mock_pending_user: User, mock_center: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=mock_pending_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 3),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def mock_another_post(mock_review_user: User, mock_center: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=mock_review_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 3),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def mock_climbing_history(mock_post: Post, mock_center_holds: List[CenterHold], mock_center_walls: List[CenterWall]):
    yield [
        ClimbingHistory(
            id=str(uuid.uuid4()),
            post=mock_post,
            hold_id=mock_center_holds[0].id,
            hold_url=mock_center_holds[0].img,
            difficulty=mock_center_holds[0].difficulty,
            challenge_count=3,
            wall_name=mock_center_walls[0].name,
            wall_type=mock_center_walls[0].type)
    ]


@pytest.fixture
def mock_review(mock_user: User, mock_center: Center):
    yield Review(
        id=str(uuid.uuid4()),
        user=mock_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="tag")]
    )


@pytest.fixture
def mock_not_answered_review(mock_user: User, mock_center: Center):
    yield Review(
        id=str(uuid.uuid4()),
        user=mock_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="tag")]
    )


@pytest.fixture
def mock_other_review(mock_pending_user: User, mock_center: Center):
    yield Review(
        id=str(uuid.uuid4()),
        user=mock_pending_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="tag")]
    )


@pytest.fixture
def mock_another_review(mock_review_user: User, mock_center: Center):
    yield Review(
        id=str(uuid.uuid4()),
        user=mock_review_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="other_tag")]
    )


@pytest.fixture
def mock_review_answer(mock_review: Review):
    yield ReviewAnswer(
        id=str(uuid.uuid4()),
        review=mock_review,
        content="answer",
        created_at=datetime(2023, 2, 7)
    )


@pytest.fixture
def mock_another_review_answer(mock_another_review: Review):
    yield ReviewAnswer(
        id=str(uuid.uuid4()),
        review=mock_another_review,
        content="answer",
        created_at=datetime(2023, 2, 7)
    )


@pytest.fixture
def mock_new_review_answer(mock_not_answered_review: Review):
    yield ReviewAnswer(
        id=str(uuid.uuid4()),
        review=mock_not_answered_review,
        content="new answer",
        created_at=datetime(2023, 2, 7)
    )


@pytest.mark.asyncio
async def test_find_posts_by_center_without_hold(session: AsyncSession,
                                                 mock_repo: dict,
                                                 mock_center: Center,
                                                 mock_post: Post,
                                                 center_service: CenterService):
    # given
    params = Params(page=1, size=10)
    post_page = Page(items=[mock_post], params=params, total=1)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["post"].find_posts_by_center.side_effect = post_page
    mock_pagination = Pagination(
        next_page_num=2,
        previous_page_num=0,
        total_num=1,
        results=[PostBriefResponseDto.from_entity(mock_post)]
    )
    mock_repo["pagination_factory"].create.side_effect = [mock_pagination]

    # when
    pages: Pagination[PostBriefResponseDto] = await center_service.find_posts_by_center(
        session=session,
        params=params,
        center_id=mock_center.id,
        hold_id=None,
        start=datetime(2022, 4, 1),
        end=datetime(2023, 3, 31)
    )

    # then
    assert len(pages.results) == 1
    assert pages.results[0].post_id == mock_post.id
    assert pages.results[0].content == mock_post.content
    assert pages.results[0].image == mock_post.img[0].url
    assert pages.results[0].created_at == get_relative_time(mock_post.created_at)
    assert pages.results[0].user_id == mock_post.user.id
    assert pages.results[0].user_nickname == mock_post.user.nickname


@pytest.mark.asyncio
async def test_find_posts_by_center_with_hold(session: AsyncSession,
                                              mock_repo: dict,
                                              mock_center: Center,
                                              mock_climbing_history: List[ClimbingHistory],
                                              mock_post: Post,
                                              center_service: CenterService):
    # given
    params = Params(page=1, size=10)
    post_page = Page(items=[mock_post], params=params, total=1)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["post"].find_posts_by_center.side_effect = post_page
    mock_pagination = Pagination(
        next_page_num=2,
        previous_page_num=0,
        total_num=1,
        results=[PostBriefResponseDto.from_entity(mock_post)]
    )
    mock_repo["pagination_factory"].create.side_effect = [mock_pagination]

    # when
    pages: Pagination[PostBriefResponseDto] = await center_service.find_posts_by_center(
        session,
        params,
        mock_center.id,
        mock_climbing_history[0].hold_id,
        datetime(2022, 4, 1),
        datetime(2023, 3, 31)
    )

    # then
    assert len(pages.results) == 1
    assert pages.results[0].post_id == mock_post.id
    assert pages.results[0].content == mock_post.content
    assert pages.results[0].image == mock_post.img[0].url
    assert pages.results[0].created_at == get_relative_time(mock_post.created_at)
    assert pages.results[0].user_id == mock_post.user.id
    assert pages.results[0].user_nickname == mock_post.user.nickname


@pytest.mark.asyncio
async def test_find_posts_by_center_with_wrong_center_id(session: AsyncSession,
                                                         mock_repo: dict,
                                                         center_service: CenterService):
    # given
    center_id = "not_existing_id"
    mock_repo["center"].find_by_id.side_effect = [None]
    params = Params(page=1, size=10)

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.find_posts_by_center(
            session,
            params,
            center_id,
            None,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31)
        )

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_find_posts_by_center_not_included_hold_in_center(session: AsyncSession,
                                                                mock_repo: dict,
                                                                mock_center: Center,
                                                                center_service: CenterService):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    params = Params(page=1, size=10)

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.find_posts_by_center(
            session,
            params,
            mock_center.id,
            "not included hold",
            datetime(2022, 4, 1),
            datetime(2023, 3, 31)
        )

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_find_posts_by_center_not_center_admin(session: AsyncSession,
                                                     mock_repo: dict,
                                                     mock_another_center: Center,
                                                     mock_climbing_history: ClimbingHistory,
                                                     center_service: CenterService):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_another_center]
    params = Params(page=1, size=10)

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.find_posts_by_center(
            session,
            params,
            mock_another_center.id,
            mock_climbing_history[0].hold_id,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31)
        )

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE


@pytest.mark.asyncio
async def test_find_reviews_by_center_not_filter(session: AsyncSession,
                                                 center_service: CenterService,
                                                 mock_repo: dict,
                                                 mock_user: User,
                                                 mock_pending_user: User,
                                                 mock_review_user: User,
                                                 mock_center: Center,
                                                 mock_other_post: Post,
                                                 mock_another_post: Post,
                                                 mock_review: Review,
                                                 mock_other_review: Review,
                                                 mock_another_review: Review):
    # given
    params = Params(page=1, size=10)
    items = [(mock_review, 1), (mock_other_review, 1), (mock_another_review, 1)]
    review_page = Page(items=items, params=params, total=3)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_reviews_by_center.side_effect = review_page
    mock_pagination = Pagination(
        next_page_num=2,
        previous_page_num=0,
        total_num=1,
        results=[ReviewBriefResponseDto.from_entity(item) for item in items]
    )
    mock_repo["pagination_factory"].create.side_effect = [mock_pagination]

    # when
    pages: Pagination[ReviewBriefResponseDto] = await center_service.find_reviews_by_center(
        session,
        params,
        mock_center.id,
        datetime(2022, 4, 1),
        datetime(2023, 3, 31),
        None,
        None
    )

    # then
    assert len(pages.results) == 3
    assert pages.results[0].content == mock_review.content
    assert pages.results[0].created_at == get_relative_time(mock_review.created_at)
    assert pages.results[0].user_id == mock_user.id == mock_review.user.id
    assert pages.results[0].user_nickname == mock_review.user.nickname
    assert pages.results[0].user_profile_image == mock_review.user.profile_img
    assert pages.results[0].user_visit_count == 1
    assert pages.results[0].tags[0] == mock_review.tag[0].word
    assert pages.results[1].user_id == mock_pending_user.id == mock_other_review.user.id == mock_other_post.user.id
    assert pages.results[2].user_id == mock_review_user.id == mock_another_review.user.id == mock_another_post.user.id


@pytest.mark.asyncio
async def test_find_reviews_by_center_not_answered(session: AsyncSession,
                                                   center_service: CenterService,
                                                   mock_repo: dict,
                                                   mock_pending_user: User,
                                                   mock_center: Center,
                                                   mock_other_review: Review):
    # given
    params = Params(page=1, size=10)
    items = [(mock_other_review, 1)]
    review_page = Page(items=items, params=params, total=0)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_reviews_by_center.side_effect = review_page
    mock_pagination = Pagination(
        next_page_num=2,
        previous_page_num=0,
        total_num=1,
        results=[ReviewBriefResponseDto.from_entity(item) for item in items]
    )
    mock_repo["pagination_factory"].create.side_effect = [mock_pagination]

    # when
    pages: Pagination[ReviewBriefResponseDto] = await center_service.find_reviews_by_center(
        session,
        params,
        mock_center.id,
        datetime(2022, 4, 1),
        datetime(2023, 3, 31),
        None,
        False
    )

    # then
    assert len(pages.results) == 1
    assert pages.results[0].content == mock_other_review.content
    assert pages.results[0].created_at == get_relative_time(mock_other_review.created_at)
    assert pages.results[0].user_id == mock_pending_user.id == mock_other_review.user.id
    assert pages.results[0].user_nickname == mock_other_review.user.nickname
    assert pages.results[0].user_profile_image == mock_other_review.user.profile_img
    assert pages.results[0].user_visit_count == 1
    assert pages.results[0].tags[0] == mock_other_review.tag[0].word


@pytest.mark.asyncio
async def test_find_reviews_by_center_with_tag(session: AsyncSession,
                                               center_service: CenterService,
                                               mock_repo: dict,
                                               mock_user: User,
                                               mock_review_user: User,
                                               mock_center: Center,
                                               mock_post: Post,
                                               mock_another_post: Post,
                                               mock_review: Review,
                                               mock_another_review: Review):
    # given
    params = Params(page=1, size=10)
    items = [(mock_review, 1), (mock_another_review, 1)]
    review_page = Page(items=items, params=params, total=0)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_reviews_by_center.side_effect = review_page
    mock_pagination = Pagination(
        next_page_num=2,
        previous_page_num=0,
        total_num=1,
        results=[ReviewBriefResponseDto.from_entity(item) for item in items]
    )
    mock_repo["pagination_factory"].create.side_effect = [mock_pagination]

    # when
    pages: Pagination[ReviewBriefResponseDto] = await center_service.find_reviews_by_center(
        session,
        params,
        mock_center.id,
        datetime(2022, 4, 1),
        datetime(2023, 3, 31),
        "tag",
        None,
    )

    # then
    assert len(pages.results) == 2
    assert pages.results[0].content == mock_review.content
    assert pages.results[0].created_at == get_relative_time(mock_review.created_at)
    assert pages.results[0].user_id == mock_user.id == mock_review.user.id == mock_post.user.id
    assert pages.results[0].user_nickname == mock_review.user.nickname
    assert pages.results[0].user_profile_image == mock_review.user.profile_img
    assert pages.results[0].user_visit_count == 1
    assert pages.results[0].tags[0] == mock_review.tag[0].word
    assert pages.results[1].user_id == mock_review_user.id == mock_another_review.user.id == mock_another_post.user.id


@pytest.mark.asyncio
async def test_find_reviews_by_center_not_exist_center(session: AsyncSession,
                                                       mock_repo: dict,
                                                       mock_center: Center,
                                                       center_service: CenterService):
    # given
    mock_repo["center"].find_by_id.side_effect = [None]
    params = Params(page=1, size=10)

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.find_reviews_by_center(
            session,
            params,
            mock_center.id,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31),
            None,
            None,
        )

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_find_reviews_by_center_not_center_admin(session: AsyncSession,
                                                       mock_repo: dict,
                                                       mock_another_center: Center,
                                                       center_service: CenterService):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_another_center]
    params = Params(page=1, size=10)

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.find_reviews_by_center(
            session,
            params,
            mock_another_center.id,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31),
            None,
            None,
        )

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE


@pytest.mark.asyncio
async def test_find_reviews_by_center_with_invalid_date(session: AsyncSession,
                                                        mock_repo: dict,
                                                        mock_another_center: Center,
                                                        center_service: CenterService):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_another_center]
    params = Params(page=1, size=10)

    with pytest.raises(BadRequestException) as exception:
        # when
        await center_service.find_reviews_by_center(
            session,
            params,
            mock_another_center.id,
            datetime(2023, 4, 1),
            datetime(2022, 3, 31),
            None,
            None,
        )

    # then
    assert exception.value.code == ErrorCode.WRONG_DATE_RANGE


@pytest.mark.asyncio
async def test_create_review_answer(session: AsyncSession,
                                    center_service: CenterService,
                                    mock_repo: dict,
                                    mock_center: Center,
                                    mock_not_answered_review: Review,
                                    mock_new_review_answer: ReviewAnswer):
    # given
    dto = ReviewAnswerRequestDto(
        answer_content="new answer"
    )

    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [mock_not_answered_review]
    mock_repo["review_answer"].find_by_review_id.side_effect = [None]
    mock_repo["review_answer"].save.side_effect = [mock_new_review_answer]

    # when
    result: ReviewAnswerResponseDto = await center_service.create_review_answer(
        session,
        dto,
        mock_center.id,
        mock_not_answered_review.id
    )

    # then
    assert result.review_id == mock_not_answered_review.id


@pytest.mark.asyncio
async def test_update_review_answer(session: AsyncSession,
                                    center_service: CenterService,
                                    mock_repo: dict,
                                    mock_center: Center,
                                    mock_review: Review,
                                    mock_review_answer: ReviewAnswer):
    # given
    dto = ReviewAnswerRequestDto(
        answer_content="updated answer"
    )

    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [mock_review]
    mock_repo["review_answer"].find_by_review_id.side_effect = [mock_review_answer]

    mock_review_answer.content = dto.answer_content
    mock_repo["review_answer"].update.side_effect = [mock_review_answer]

    # when
    result: ReviewAnswerResponseDto = await center_service.update_review_answer(
        session,
        dto,
        mock_center.id,
        mock_review.id
    )

    # then
    assert result.content == mock_review_answer.content == "updated answer"


@pytest.mark.asyncio
async def test_delete_review_answer(session: AsyncSession,
                                    center_service: CenterService,
                                    mock_repo: dict,
                                    mock_center: Center,
                                    mock_review: Review,
                                    mock_review_answer: ReviewAnswer):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [mock_review]
    mock_repo["review_answer"].find_by_review_id.side_effect = [mock_review_answer]
    mock_repo["review_answer"].delete.side_effect = [mock_review_answer]

    # when
    result = await center_service.delete_review_answer(
        session,
        mock_center.id,
        mock_review.id
    )

    # then
    assert result is mock_review_answer


@pytest.mark.asyncio
async def test_create_review_answer_with_not_exist_center(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_review: Review
):
    # given
    mock_repo["center"].find_by_id.side_effect = [None]
    wrong_id = "wrong id"
    dto = ReviewAnswerRequestDto(answer_content="content")

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.create_review_answer(session, dto, wrong_id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_create_review_answer_with_not_center_admin(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_another_center: Center,
        mock_review: Review
):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_another_center]
    dto = ReviewAnswerRequestDto(answer_content="content")

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.create_review_answer(session, dto, mock_another_center.id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE


@pytest.mark.asyncio
async def test_create_review_answer_with_not_exist_review(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center
):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [None]
    dto = ReviewAnswerRequestDto(answer_content="content")
    wrong_review_id = "wrong id"

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.create_review_answer(session, dto, mock_center.id, wrong_review_id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_create_review_answer_with_already_exist_answer(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review,
        mock_review_answer: ReviewAnswer
):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [mock_review]
    mock_repo["review_answer"].find_by_review_id.side_effect = [mock_review_answer]
    dto = ReviewAnswerRequestDto(answer_content="content")

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.create_review_answer(session, dto, mock_center.id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.ROW_ALREADY_EXIST


@pytest.mark.asyncio
async def test_update_review_answer_with_not_exist_center(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_review: Review
):
    # given
    mock_repo["center"].find_by_id.side_effect = [None]
    wrong_id = "wrong id"
    dto = ReviewAnswerRequestDto(answer_content="content")

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.update_review_answer(session, dto, wrong_id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_update_review_answer_with_not_center_admin(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_another_center: Center,
        mock_review: Review
):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_another_center]
    dto = ReviewAnswerRequestDto(answer_content="content")

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.update_review_answer(session, dto, mock_another_center.id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE


@pytest.mark.asyncio
async def test_update_review_answer_with_not_exist_review(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center
):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [None]
    dto = ReviewAnswerRequestDto(answer_content="content")
    wrong_review_id = "wrong id"

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.update_review_answer(session, dto, mock_center.id, wrong_review_id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_update_review_answer_with_not_exist_answer(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review
):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [mock_review]
    mock_repo["review_answer"].find_by_review_id.side_effect = [None]
    dto = ReviewAnswerRequestDto(answer_content="content")

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.update_review_answer(session, dto, mock_center.id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_delete_review_answer_with_not_exist_center(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_review: Review
):
    # given
    mock_repo["center"].find_by_id.side_effect = [None]
    wrong_id = "wrong id"

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.delete_review_answer(session, wrong_id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_delete_review_answer_with_not_center_admin(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_another_center: Center,
        mock_review: Review
):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_another_center]

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.delete_review_answer(session, mock_another_center.id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE


@pytest.mark.asyncio
async def test_delete_review_answer_with_not_exist_review(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center
):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [None]
    wrong_review_id = "wrong id"

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.delete_review_answer(session, mock_center.id, wrong_review_id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_delete_review_answer_with_not_exist_answer(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review
):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [mock_review]
    mock_repo["review_answer"].find_by_review_id.side_effect = [None]

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.delete_review_answer(session, mock_center.id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
@patch("claon_admin.service.center.upload_file")
async def test_upload_file_with_purpose(mock_upload_file,
                                        center_service: CenterService):
    # given
    upload_file = AsyncMock(spec=UploadFile)
    upload_file.filename = "test.png"
    mock_upload_file.return_value = "https://test_upload_center/center/image/uuid.png"
    purpose = CenterUploadPurpose.IMAGE

    # when
    result: UploadFileResponseDto = await center_service.upload_file(purpose, upload_file)

    # then
    assert result.file_url.split('.')[-1] == "png"
    assert result.file_url.split('/')[-2] == "image"
    assert result.file_url.split('/')[-3] == "center"


@pytest.mark.asyncio
@patch("claon_admin.service.center.upload_file")
async def test_upload_file_with_purpose_proof(mock_upload_file,
                                              center_service: CenterService):
    # given
    upload_file = AsyncMock(spec=UploadFile)
    upload_file.filename = "test.pdf"
    mock_upload_file.return_value = "https://test_upload_center_proof/center/proof/uuid.pdf"
    purpose = CenterUploadPurpose.PROOF

    # when
    result: UploadFileResponseDto = await center_service.upload_file(purpose, upload_file)

    # then
    assert result.file_url.split('.')[-1] == "pdf"
    assert result.file_url.split('/')[-2] == "proof"
    assert result.file_url.split('/')[-3] == "center"


@pytest.mark.asyncio
async def test_upload_file_with_invalid_format(center_service: CenterService):
    # given
    upload_file = AsyncMock(spec=UploadFile)
    upload_file.filename = "test.gif"
    purpose = CenterUploadPurpose.PROOF

    with pytest.raises(BadRequestException) as exception:
        # when
        await center_service.upload_file(purpose, upload_file)

    # then
    assert exception.value.code == ErrorCode.INVALID_FORMAT


@pytest.mark.asyncio
async def test_upload_file_with_second_invalid_format(center_service: CenterService):
    # given
    upload_file = AsyncMock(spec=UploadFile)
    upload_file.filename = "test.pdf"
    purpose = CenterUploadPurpose.IMAGE

    with pytest.raises(BadRequestException) as exception:
        # when
        await center_service.upload_file(purpose, upload_file)

    # then
    assert exception.value.code == ErrorCode.INVALID_FORMAT


async def test_find_centers_by_name(
        session: AsyncSession,
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_another_center: Center
):
    # given
    response = CenterNameResponseDto.from_entity(mock_center)
    another_response = CenterNameResponseDto.from_entity(mock_another_center)
    mock_repo["center"].find_by_name.side_effect = [[mock_center, mock_another_center]]

    # when
    result = await center_service.find_centers_by_name(session, mock_center.name)

    # then
    assert len(result) == 2
    assert response in result
    assert another_response in result
