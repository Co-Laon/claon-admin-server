import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.center import Center, CenterSchedule
from tests.repository.center.conftest import center_schedule_repository


@pytest.mark.describe("Test case for center schedule repository")
class TestCenterScheduleRepository(object):
    @pytest.mark.asyncio
    async def test_find_by_center(
            self,
            session: AsyncSession,
            center_fixture: Center,
            center_schedule_fixture: CenterSchedule
    ):
         # when
        center_schedules = await center_schedule_repository.find_by_center(session, center_fixture.id)

        # then
        assert center_schedules == [center_schedule_fixture]
