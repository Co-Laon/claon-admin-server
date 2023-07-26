from unittest.mock import patch

import pytest
from fastapi_pagination import Params, Page

from claon_admin.common.util.pagination import Pagination
from claon_admin.model.user import UserNameResponseDto
from claon_admin.schema.user import User
from claon_admin.service.user import UserService


@pytest.mark.describe("Test case for find all by nickname")
class TestFindAllByNickname(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    @patch("claon_admin.common.util.pagination.paginate")
    async def test_find_all_by_nickname(
            self,
            mock_paginate,
            user_service: UserService,
            mock_repo: dict,
            user_fixture: User,
            other_user_fixture: User
    ):
        # given
        nickname = "nickname"
        params = Params(page=1, size=10)
        items = [user_fixture, other_user_fixture]
        result_page = Page(items=items, params=params, total=2, page=1, pages=1)
        mock_repo["user"].find_all_by_nickname.return_value = result_page
        mock_pagination = Pagination(
            next_page_num=2,
            previous_page_num=0,
            total_num=1,
            results=[UserNameResponseDto.from_entity(entity=user) for user in items]
        )
        mock_paginate.return_value = [mock_pagination]

        # when
        pages = await user_service.find_all_by_nickname(nickname=nickname, params=params)

        # then
        assert len(pages.results) == 2
        