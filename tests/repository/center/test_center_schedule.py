from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.center import Center, CenterSchedule


@pytest.mark.describe("Test case for center schedule repository")
class TestCenterScheduleRepository(object):
    @pytest.mark.asyncio
    async def test_save_schedule(
            self,
            session: AsyncSession,
            center_fixture: Center,
            schedule_fixture: CenterSchedule
    ):
        # then
        assert schedule_fixture.center == center_fixture
        assert schedule_fixture.title == "title"
        assert schedule_fixture.start_time == datetime(2023, 10, 1, 10, 0)
        assert schedule_fixture.end_time == datetime(2023, 10, 2, 10, 0)
        assert schedule_fixture.description == "test"
