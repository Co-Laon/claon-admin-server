from datetime import datetime, timedelta

import pytest
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import WallType
from claon_admin.common.util.time import now
from claon_admin.schema.center import Center
from claon_admin.schema.post import Post, ClimbingHistory
from claon_admin.schema.user import User
from tests.repository.post.conftest import post_repository


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
            now() - timedelta(days=1),
            now()
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
            now() - timedelta(days=1),
            now()
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
            start=now() - timedelta(days=1),
            end=now()
        ) == Page.create(items=[post_fixture], params=params, total=1)

    @pytest.mark.asyncio
    async def test_count_by_center_and_date(
            self,
            session: AsyncSession,
            center_fixture: Center,
            another_center_fixture: Center,
            post_fixture: Post,
            another_post_fixture: Post,
            other_post_fixture: Post
    ):
        # when
        result = await post_repository.count_by_center_and_date(
            session,
            [center_fixture.id, another_center_fixture.id],
            now() - timedelta(days=1),
            now()
        )

        # then
        assert len(result) == 2
        assert result[center_fixture.id] == 2
        assert result[another_center_fixture.id] == 1

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
