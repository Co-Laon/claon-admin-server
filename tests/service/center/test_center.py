from datetime import datetime
from typing import List
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import UploadFile
from fastapi_pagination import Params, Page

from claon_admin.common.enum import Role, CenterUploadPurpose
from claon_admin.common.error.exception import BadRequestException, UnauthorizedException, ErrorCode, NotFoundException
from claon_admin.common.util.pagination import Pagination
from claon_admin.common.util.time import get_relative_time
from claon_admin.model.auth import RequestUser
from claon_admin.model.file import UploadFileResponseDto
from claon_admin.model.post import PostBriefResponseDto, PostSummaryResponseDto
from claon_admin.model.review import ReviewBriefResponseDto, ReviewAnswerRequestDto, ReviewAnswerResponseDto
from claon_admin.model.center import CenterNameResponseDto, CenterBriefResponseDto
from claon_admin.schema.center import Center, Post, ClimbingHistory, Review, ReviewAnswer
from claon_admin.schema.user import User
from claon_admin.service.center import CenterService


@pytest.mark.asyncio
async def test_find_posts_by_center_without_hold(
        mock_repo: dict,
        mock_center: Center,
        mock_post: Post,
        center_service: CenterService
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
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
        session=None,
        subject=request_user,
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
async def test_find_posts_by_center_with_hold(
        mock_repo: dict,
        mock_center: Center,
        mock_climbing_history: List[ClimbingHistory],
        mock_post: Post,
        center_service: CenterService
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
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
        None,
        request_user,
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
async def test_find_posts_by_center_with_wrong_center_id(
        mock_repo: dict,
        mock_center: Center,
        center_service: CenterService
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    center_id = "not_existing_id"
    mock_repo["center"].find_by_id.side_effect = [None]
    params = Params(page=1, size=10)

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.find_posts_by_center(
            None,
            request_user,
            params,
            center_id,
            None,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31)
        )

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_find_posts_by_center_not_included_hold_in_center(
        mock_repo: dict,
        mock_center: Center,
        center_service: CenterService
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    params = Params(page=1, size=10)

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.find_posts_by_center(
            None,
            request_user,
            params,
            mock_center.id,
            "not included hold",
            datetime(2022, 4, 1),
            datetime(2023, 3, 31)
        )

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_find_posts_by_center_not_center_admin(
        mock_repo: dict,
        mock_center: Center,
        mock_climbing_history: ClimbingHistory,
        center_service: CenterService
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    params = Params(page=1, size=10)

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.find_posts_by_center(
            None,
            request_user,
            params,
            mock_center.id,
            mock_climbing_history[0].hold_id,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31)
        )

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE


@pytest.mark.asyncio
async def test_find_reviews_by_center_not_filter(
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
        mock_another_review: Review
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
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
        None,
        request_user,
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
async def test_find_reviews_by_center_not_answered(
        center_service: CenterService,
        mock_repo: dict,
        mock_pending_user: User,
        mock_center: Center,
        mock_other_review: Review
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
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
        None,
        request_user,
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
async def test_find_reviews_by_center_with_tag(
        center_service: CenterService,
        mock_repo: dict,
        mock_user: User,
        mock_review_user: User,
        mock_center: Center,
        mock_post: Post,
        mock_another_post: Post,
        mock_review: Review,
        mock_another_review: Review
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
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
        None,
        request_user,
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
async def test_find_reviews_by_center_not_exist_center(
        mock_repo: dict,
        mock_center: Center,
        center_service: CenterService
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [None]
    params = Params(page=1, size=10)

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.find_reviews_by_center(
            None,
            request_user,
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
async def test_find_reviews_by_center_not_center_admin(
        mock_repo: dict,
        mock_center: Center,
        center_service: CenterService
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    params = Params(page=1, size=10)

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.find_reviews_by_center(
            None,
            request_user,
            params,
            mock_center.id,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31),
            None,
            None,
        )

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE


@pytest.mark.asyncio
async def test_find_reviews_by_center_with_invalid_date(
        mock_repo: dict,
        mock_center: Center,
        center_service: CenterService
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    params = Params(page=1, size=10)

    with pytest.raises(BadRequestException) as exception:
        # when
        await center_service.find_reviews_by_center(
            None,
            request_user,
            params,
            mock_center.id,
            datetime(2023, 4, 1),
            datetime(2022, 3, 31),
            None,
            None,
        )

    # then
    assert exception.value.code == ErrorCode.WRONG_DATE_RANGE


@pytest.mark.asyncio
async def test_create_review_answer(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_not_answered_review: Review,
        mock_new_review_answer: ReviewAnswer
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    dto = ReviewAnswerRequestDto(
        answer_content="new answer"
    )

    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [mock_not_answered_review]
    mock_repo["review_answer"].find_by_review_id.side_effect = [None]
    mock_repo["review_answer"].save.side_effect = [mock_new_review_answer]

    # when
    result: ReviewAnswerResponseDto = await center_service.create_review_answer(
        None,
        request_user,
        dto,
        mock_center.id,
        mock_not_answered_review.id
    )

    # then
    assert result.review_id == mock_not_answered_review.id


@pytest.mark.asyncio
async def test_update_review_answer(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review,
        mock_review_answer: ReviewAnswer
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
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
        None,
        request_user,
        dto,
        mock_center.id,
        mock_review.id
    )

    # then
    assert result.content == mock_review_answer.content == "updated answer"


@pytest.mark.asyncio
async def test_delete_review_answer(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review,
        mock_review_answer: ReviewAnswer
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [mock_review]
    mock_repo["review_answer"].find_by_review_id.side_effect = [mock_review_answer]
    mock_repo["review_answer"].delete.side_effect = [mock_review_answer]

    # when
    result = await center_service.delete_review_answer(
        None,
        request_user,
        mock_center.id,
        mock_review.id
    )

    # then
    assert result is mock_review_answer


@pytest.mark.asyncio
async def test_create_review_answer_with_not_exist_center(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [None]
    wrong_id = "wrong id"
    dto = ReviewAnswerRequestDto(answer_content="content")

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.create_review_answer(None, request_user, dto, wrong_id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_create_review_answer_with_not_center_admin(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    dto = ReviewAnswerRequestDto(answer_content="content")

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.create_review_answer(None, request_user, dto, mock_center.id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE


@pytest.mark.asyncio
async def test_create_review_answer_with_not_exist_review(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [None]
    dto = ReviewAnswerRequestDto(answer_content="content")
    wrong_review_id = "wrong id"

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.create_review_answer(None, request_user, dto, mock_center.id, wrong_review_id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_create_review_answer_with_already_exist_answer(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review,
        mock_review_answer: ReviewAnswer
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [mock_review]
    mock_repo["review_answer"].find_by_review_id.side_effect = [mock_review_answer]
    dto = ReviewAnswerRequestDto(answer_content="content")

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.create_review_answer(None, request_user, dto, mock_center.id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.ROW_ALREADY_EXIST


@pytest.mark.asyncio
async def test_update_review_answer_with_not_exist_center(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [None]
    wrong_id = "wrong id"
    dto = ReviewAnswerRequestDto(answer_content="content")

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.update_review_answer(None, request_user, dto, wrong_id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_update_review_answer_with_not_center_admin(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    dto = ReviewAnswerRequestDto(answer_content="content")

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.update_review_answer(None, request_user, dto, mock_center.id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE


@pytest.mark.asyncio
async def test_update_review_answer_with_not_exist_review(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [None]
    dto = ReviewAnswerRequestDto(answer_content="content")
    wrong_review_id = "wrong id"

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.update_review_answer(None, request_user, dto, mock_center.id, wrong_review_id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_update_review_answer_with_not_exist_answer(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [mock_review]
    mock_repo["review_answer"].find_by_review_id.side_effect = [None]
    dto = ReviewAnswerRequestDto(answer_content="content")

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.update_review_answer(None, request_user, dto, mock_center.id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_delete_review_answer_with_not_exist_center(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [None]
    wrong_id = "wrong id"

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.delete_review_answer(None, request_user, wrong_id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_delete_review_answer_with_not_center_admin(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.delete_review_answer(None, request_user, mock_center.id, mock_review.id)

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE


@pytest.mark.asyncio
async def test_delete_review_answer_with_not_exist_review(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [None]
    wrong_review_id = "wrong id"

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.delete_review_answer(None, request_user, mock_center.id, wrong_review_id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_delete_review_answer_with_not_exist_answer(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_review: Review
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["review"].find_by_id_and_center_id.side_effect = [mock_review]
    mock_repo["review_answer"].find_by_review_id.side_effect = [None]

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.delete_review_answer(None, request_user, mock_center.id, mock_review.id)

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
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center
):
    # given
    response = CenterNameResponseDto.from_entity(mock_center)
    mock_repo["center"].find_by_name.side_effect = [[mock_center]]

    # when
    result = await center_service.find_centers_by_name(None, mock_center.name)

    # then
    assert len(result) == 1
    assert response in result


@pytest.mark.asyncio
async def test_find_posts_summary_by_center(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_yesterday_post: Post,
        mock_today_post: Post,
        mock_other_post: Post,
        mock_another_post: Post,
        mock_post: Post
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["post"].find_posts_summary_by_center.side_effect = [
        {
            "today": 1,
            "week": 2,
            "month": 2,
            "total": 4,
            "per_day": [(mock_yesterday_post.id, mock_yesterday_post.created_at)],
            "per_week": [(mock_post.id, mock_post.created_at),
                         (mock_other_post.id, mock_other_post.created_at),
                         (mock_another_post.id, mock_another_post.created_at),
                         (mock_yesterday_post.id, mock_yesterday_post.created_at)]
        }
    ]

    # when
    results: PostSummaryResponseDto = await center_service.find_posts_summary_by_center(None,
                                                                                        request_user,
                                                                                        mock_center.id)

    # then
    assert results.center_id == mock_center.id
    assert results.center_name == mock_center.name
    assert results.count_today == 1
    assert results.count_week == 2
    assert results.count_month == 2
    assert results.count_total == 4
    assert len(results.count_per_day) == 7
    assert results.count_per_day[5].count == 0
    assert results.count_per_day[6].count == 1
    assert len(results.count_per_week) == 52


@pytest.mark.asyncio
async def test_find_posts_summary_by_center_with_not_exist_center(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center
):
    # given
    request_user = RequestUser(id=mock_center.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [None]
    wrong_id = "wrong id"

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.find_posts_summary_by_center(None, request_user, wrong_id)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_find_posts_summary_by_center_with_not_center_admin(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
    mock_repo["center"].find_by_id.side_effect = [mock_center]

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.find_posts_summary_by_center(None, request_user, mock_center.id)

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE


@pytest.mark.asyncio
async def test_find_centers(
        center_service: CenterService,
        mock_repo: dict,
        mock_center: Center,
        mock_other_center: Center
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
    params = Params(page=1, size=10)
    items = [mock_center, mock_other_center]
    center_page = Page(items=items, params=params, total=2)
    mock_repo["center"].find_all_by_user_id.return_value = center_page
    mock_pagination = Pagination(
        next_page_num=2,
        previous_page_num=0,
        total_num=1,
        results=[CenterBriefResponseDto.from_entity(item) for item in items]
    )
    mock_repo["pagination_factory"].create.side_effect = [mock_pagination]

    # when
    pages: Pagination[CenterBriefResponseDto] = await center_service.find_centers(
        None,
        params=params,
        subject=request_user
    )

    # then
    assert len(pages.results) == 2
    assert pages.results[0].center_id == mock_center.id
    assert pages.results[1].center_id == mock_other_center.id


@pytest.mark.asyncio
async def test_find_centers_with_not_center_admin(
        center_service: CenterService,
        mock_repo: dict
):
    # given
    request_user = RequestUser(id="111111", sns="test@claon.com", role=Role.LECTOR)
    params = Params(page=1, size=10)

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.find_centers(None, params, request_user)

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE


@pytest.mark.asyncio
async def test_find_centers_with_not_exist_center(
        center_service: CenterService,
        mock_repo: dict
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
    params = Params(page=1, size=10)
    items = []
    center_page = Page(items=items, params=params, total=0)
    mock_repo["center"].find_all_by_user_id.return_value = center_page

    with pytest.raises(NotFoundException) as exception:
        # when
        await center_service.find_centers(None, params, request_user)

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST
