from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi_pagination import Params, Page

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException, BadRequestException
from claon_admin.common.util.pagination import Pagination
from claon_admin.common.util.time import get_relative_time
from claon_admin.model.auth import RequestUser
from claon_admin.model.review import ReviewBriefResponseDto
from claon_admin.schema.center import Center, Post, Review
from claon_admin.schema.user import User
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for find reviews by center")
class TestFindReviewsByCenter(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    @patch("claon_admin.common.util.pagination.paginate")
    async def test_find_reviews_by_center_not_filter(
            self,
            mock_paginate,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            pending_user_fixture: User,
            review_user_fixture: User,
            center_fixture: Center,
            other_post_fixture: Post,
            another_post_fixture: Post,
            review_fixture: Review,
            other_review_fixture: Review,
            another_review_fixture: Review
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        params = Params(page=1, size=10)
        items = [(review_fixture, 1), (other_review_fixture, 1), (another_review_fixture, 1)]
        review_page = Page(items=items, params=params, total=3, page=1, pages=1)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["review"].find_reviews_by_center.return_value = review_page
        mock_pagination = Pagination(
            next_page_num=2,
            previous_page_num=0,
            total_num=1,
            results=[ReviewBriefResponseDto.from_entity(item) for item in items]
        )
        mock_paginate.return_value = [mock_pagination]

        # when
        pages: Pagination[ReviewBriefResponseDto] = await center_service.find_reviews_by_center(
            request_user,
            params,
            center_fixture.id,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31),
            None,
            None
        )

        # then
        assert len(pages.results) == 3
        assert pages.results[0].content == review_fixture.content
        assert pages.results[0].created_at == get_relative_time(review_fixture.created_at)
        assert pages.results[0].user_id == user_fixture.id == review_fixture.user.id
        assert pages.results[0].user_nickname == review_fixture.user.nickname
        assert pages.results[0].user_profile_image == review_fixture.user.profile_img
        assert pages.results[0].user_visit_count == 1
        assert pages.results[0].tags[0] == review_fixture.tag[0].word
        assert pages.results[1].user_id \
               == pending_user_fixture.id == other_review_fixture.user.id == other_post_fixture.user.id
        assert pages.results[2].user_id \
               == review_user_fixture.id == another_review_fixture.user.id == another_post_fixture.user.id

    @pytest.mark.asyncio
    @pytest.mark.it("Success case: not answered")
    @patch("claon_admin.common.util.pagination.paginate")
    async def test_find_reviews_by_center_not_answered(
            self,
            mock_paginate,
            center_service: CenterService,
            mock_repo: dict,
            pending_user_fixture: User,
            center_fixture: Center,
            other_review_fixture: Review
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        params = Params(page=1, size=10)
        items = [(other_review_fixture, 1)]
        review_page = Page(items=items, params=params, total=0, page=1, pages=1)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["review"].find_reviews_by_center.return_value = review_page
        mock_pagination = Pagination(
            next_page_num=2,
            previous_page_num=0,
            total_num=1,
            results=[ReviewBriefResponseDto.from_entity(item) for item in items]
        )
        mock_paginate.return_value = [mock_pagination]

        # when
        pages: Pagination[ReviewBriefResponseDto] = await center_service.find_reviews_by_center(
            request_user,
            params,
            center_fixture.id,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31),
            None,
            False
        )

        # then
        assert len(pages.results) == 1
        assert pages.results[0].content == other_review_fixture.content
        assert pages.results[0].created_at == get_relative_time(other_review_fixture.created_at)
        assert pages.results[0].user_id == pending_user_fixture.id == other_review_fixture.user.id
        assert pages.results[0].user_nickname == other_review_fixture.user.nickname
        assert pages.results[0].user_profile_image == other_review_fixture.user.profile_img
        assert pages.results[0].user_visit_count == 1
        assert pages.results[0].tags[0] == other_review_fixture.tag[0].word

    @pytest.mark.asyncio
    @pytest.mark.it("Success case: with tag")
    @patch("claon_admin.common.util.pagination.paginate")
    async def test_find_reviews_by_center_with_tag(
            self,
            mock_paginate,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            review_user_fixture: User,
            center_fixture: Center,
            post_fixture: Post,
            another_post_fixture: Post,
            review_fixture: Review,
            another_review_fixture: Review
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        params = Params(page=1, size=10)
        items = [(review_fixture, 1), (another_review_fixture, 1)]
        review_page = Page(items=items, params=params, total=0, page=1, pages=1)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["review"].find_reviews_by_center.return_value = review_page
        mock_pagination = Pagination(
            next_page_num=2,
            previous_page_num=0,
            total_num=1,
            results=[ReviewBriefResponseDto.from_entity(item) for item in items]
        )
        mock_paginate.return_value = [mock_pagination]

        # when
        pages: Pagination[ReviewBriefResponseDto] = await center_service.find_reviews_by_center(
            request_user,
            params,
            center_fixture.id,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31),
            "tag",
            None,
        )

        # then
        assert len(pages.results) == 2
        assert pages.results[0].content == review_fixture.content
        assert pages.results[0].created_at == get_relative_time(review_fixture.created_at)
        assert pages.results[0].user_id == user_fixture.id == review_fixture.user.id == post_fixture.user.id
        assert pages.results[0].user_nickname == review_fixture.user.nickname
        assert pages.results[0].user_profile_image == review_fixture.user.profile_img
        assert pages.results[0].user_visit_count == 1
        assert pages.results[0].tags[0] == review_fixture.tag[0].word
        assert pages.results[
                   1].user_id == review_user_fixture.id == another_review_fixture.user.id == another_post_fixture.user.id

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_find_reviews_by_center_not_exist_center(
            self,
            mock_repo: dict,
            center_fixture: Center,
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [None]
        params = Params(page=1, size=10)

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.find_reviews_by_center(
                request_user,
                params,
                center_fixture.id,
                datetime(2022, 4, 1),
                datetime(2023, 3, 31),
                None,
                None,
            )

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request user is not center admin")
    async def test_find_reviews_by_center_not_center_admin(
            self,
            mock_repo: dict,
            center_fixture: Center,
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        params = Params(page=1, size=10)

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.find_reviews_by_center(
                request_user,
                params,
                center_fixture.id,
                datetime(2022, 4, 1),
                datetime(2023, 3, 31),
                None,
                None,
            )

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: invalid date range")
    async def test_find_reviews_by_center_with_invalid_date(
            self,
            mock_repo: dict,
            center_fixture: Center,
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        params = Params(page=1, size=10)

        with pytest.raises(BadRequestException) as exception:
            # when
            await center_service.find_reviews_by_center(
                request_user,
                params,
                center_fixture.id,
                datetime(2023, 4, 1),
                datetime(2022, 3, 31),
                None,
                None,
            )

        # then
        assert exception.value.code == ErrorCode.WRONG_DATE_RANGE
