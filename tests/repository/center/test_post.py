from datetime import datetime

import pytest
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import WallType
from claon_admin.schema.center import Post, Center, ClimbingHistory
from claon_admin.schema.user import User
from tests.repository.center.conftest import post_repository


@pytest.mark.describe("Test case for post repository")
class TestPostRepository(object):
    @pytest.mark.asyncio
    async def test_save_post(
            self,
            session: AsyncSession,
            user_fixture: User,
            post_fixture: Post
    ):
        assert post_fixture.user == user_fixture
        assert post_fixture.content == "content"
        assert post_fixture.img[0].url == "url"
        assert post_fixture.created_at == datetime(2023, 1, 1)

    @pytest.mark.asyncio
    async def test_find_posts_by_center(
            self,
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
            self,
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
            self,
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
            self,
            session: AsyncSession,
            center_fixture: Center,
            post_fixture: Post
    ):
        # then
        assert await post_repository.find_posts_summary_by_center(session, center_fixture.id) \
               == {
                   "today": 0,
                   "week": 0,
                   "month": 0,
                   "total": 1,
                   "per_day": [],
                   "per_week": [(post_fixture.id, post_fixture.created_at)]
               }

    @pytest.mark.asyncio
    async def test_save_climbing_history(
            self,
            session: AsyncSession,
            post_fixture: Post,
            climbing_history_fixture: ClimbingHistory
    ):
        assert climbing_history_fixture.post == post_fixture
        assert climbing_history_fixture.difficulty == "hard"
        assert climbing_history_fixture.challenge_count == 2
        assert climbing_history_fixture.wall_name == "wall"
        assert climbing_history_fixture.wall_type == WallType.ENDURANCE.value
