from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.center import Center, CenterSchedule
from tests.repository.center.conftest import center_schedule_repository


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
        assert schedule_fixture.start_time == datetime(2023, 8, 1, 10, 0)
        assert schedule_fixture.end_time == datetime(2023, 8, 2, 10, 0)
        assert schedule_fixture.description == "test"

    @pytest.mark.asyncio
    async def test_find_by_id_and_center_id(
            self,
            session: AsyncSession,
            center_fixture: Center,
            schedule_fixture: CenterSchedule
    ):
         # when
        center_schedule = await center_schedule_repository.find_by_id_and_center_id(session, schedule_fixture.id, center_fixture.id)

        # then
        assert center_schedule == schedule_fixture

    @pytest.mark.asyncio
    async def test_find_by_center_id_and_date_from(
            self,
            session: AsyncSession,
            center_fixture: Center,
            schedule_fixture: CenterSchedule
    ):
        # given
        date_from = datetime.strptime("2023-07-30", "%Y-%m-%d").date()

        # when
        schedules = await center_schedule_repository.find_by_center_id_and_date_from(session, center_fixture.id, date_from)

        # then
        assert schedules == [schedule_fixture]
