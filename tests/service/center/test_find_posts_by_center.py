from datetime import datetime
from typing import List
from unittest.mock import patch

import pytest
from fastapi_pagination import Params, Page

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.common.util.pagination import Pagination
from claon_admin.common.util.time import get_relative_time
from claon_admin.model.auth import RequestUser
from claon_admin.model.post import PostBriefResponseDto
from claon_admin.schema.center import Center
from claon_admin.schema.post import Post, ClimbingHistory
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for find posts by center")
class TestFindPostsByCenter(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case: without hold")
    @patch("claon_admin.common.util.pagination.paginate")
    async def test_find_posts_by_center_without_hold(
            self,
            mock_paginate,
            mock_repo: dict,
            center_fixture: Center,
            post_fixture: Post,
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        params = Params(page=1, size=10)
        post_page = Page(items=[post_fixture], params=params, total=1, page=1, pages=1)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["post"].find_posts_by_center.return_value = post_page
        mock_pagination = Pagination(
            next_page_num=2,
            previous_page_num=0,
            total_num=1,
            results=[PostBriefResponseDto.from_entity(post_fixture)]
        )
        mock_paginate.return_value = [mock_pagination]

        # when
        pages: Pagination[PostBriefResponseDto] = await center_service.find_posts_by_center(
            session=None,
            subject=request_user,
            params=params,
            center_id=center_fixture.id,
            hold_id=None,
            start=datetime(2022, 4, 1),
            end=datetime(2023, 3, 31)
        )

        # then
        assert len(pages.results) == 1
        assert pages.results[0].post_id == post_fixture.id
        assert pages.results[0].content == post_fixture.content
        assert pages.results[0].image == post_fixture.img[0].url
        assert pages.results[0].created_at == get_relative_time(post_fixture.created_at)
        assert pages.results[0].user_id == post_fixture.user.id
        assert pages.results[0].user_nickname == post_fixture.user.nickname

    @pytest.mark.asyncio
    @pytest.mark.it("Success case: with hold")
    @patch("claon_admin.common.util.pagination.paginate")
    async def test_find_posts_by_center_with_hold(
            self,
            mock_paginate,
            mock_repo: dict,
            center_fixture: Center,
            climbing_history_fixture: List[ClimbingHistory],
            post_fixture: Post,
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        params = Params(page=1, size=10)
        post_page = Page(items=[post_fixture], params=params, total=1, page=1, pages=1)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["post"].find_posts_by_center.return_value = post_page
        mock_pagination = Pagination(
            next_page_num=2,
            previous_page_num=0,
            total_num=1,
            results=[PostBriefResponseDto.from_entity(post_fixture)]
        )
        mock_paginate.return_value = [mock_pagination]

        # when
        pages: Pagination[PostBriefResponseDto] = await center_service.find_posts_by_center(
            None,
            request_user,
            params,
            center_fixture.id,
            climbing_history_fixture[0].hold_id,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31)
        )

        # then
        assert len(pages.results) == 1
        assert pages.results[0].post_id == post_fixture.id
        assert pages.results[0].content == post_fixture.content
        assert pages.results[0].image == post_fixture.img[0].url
        assert pages.results[0].created_at == get_relative_time(post_fixture.created_at)
        assert pages.results[0].user_id == post_fixture.user.id
        assert pages.results[0].user_nickname == post_fixture.user.nickname

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_find_posts_by_center_with_wrong_center_id(
            self,
            mock_repo: dict,
            center_fixture: Center,
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
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
    @pytest.mark.it("Fail case: hold in center is not found")
    async def test_find_posts_by_center_not_included_hold_in_center(
            self,
            mock_repo: dict,
            center_fixture: Center,
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        params = Params(page=1, size=10)

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.find_posts_by_center(
                None,
                request_user,
                params,
                center_fixture.id,
                "not included hold",
                datetime(2022, 4, 1),
                datetime(2023, 3, 31)
            )

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request is not center admin")
    async def test_find_posts_by_center_not_center_admin(
            self,
            mock_repo: dict,
            center_fixture: Center,
            climbing_history_fixture: ClimbingHistory,
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        params = Params(page=1, size=10)

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.find_posts_by_center(
                None,
                request_user,
                params,
                center_fixture.id,
                climbing_history_fixture[0].hold_id,
                datetime(2022, 4, 1),
                datetime(2023, 3, 31)
            )

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
