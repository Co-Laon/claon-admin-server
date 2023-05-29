from datetime import timedelta
from typing import List

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.util.time import now
from claon_admin.schema.center import Center
from claon_admin.schema.post import PostCountHistory
from tests.repository.post.conftest import post_count_history_repository


@pytest.mark.describe('Test case for post count history repository')
class TestPostCountHistoryRepository(object):
    @pytest.mark.asyncio
    async def test_save_post_count_history(
            self,
            session: AsyncSession,
            center_fixture: Center,
            post_count_history_fixture: PostCountHistory
    ):
        # then
        assert post_count_history_fixture.center_id == center_fixture.id
        assert post_count_history_fixture.count == 10
        assert post_count_history_fixture.reg_date == now().date()

    @pytest.mark.asyncio
    async def test_sum_count_by_center(
            self,
            session: AsyncSession,
            center_fixture: Center,
            post_count_history_list_fixture: List[PostCountHistory]
    ):
        # then
        assert await post_count_history_repository.sum_count_by_center(session, center_fixture.id) == 30

    @pytest.mark.asyncio
    async def test_find_by_center_and_date(
            self,
            session: AsyncSession,
            center_fixture: Center,
            post_count_history_list_fixture: List[PostCountHistory]
    ):
        # when
        result = await post_count_history_repository.find_by_center_and_date(
            session,
            center_fixture.id,
            now().date() - timedelta(weeks=52),
            now().date()
        )

        # then
        assert len(result) == len(post_count_history_list_fixture)

        for i in range(len(result)):
            assert result[i].center_id == post_count_history_list_fixture[i].center_id
            assert result[i].count == post_count_history_list_fixture[i].count
            assert result[i].reg_date == post_count_history_list_fixture[i].reg_date
