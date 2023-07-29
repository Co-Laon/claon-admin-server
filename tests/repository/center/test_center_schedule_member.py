import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.center import CenterSchedule, CenterScheduleMember
from claon_admin.schema.user import User


@pytest.mark.describe("Test case for center schedule member repository")
class TestCenterScheduleMemberRepository(object):
    @pytest.mark.asyncio
    async def test_save_schedule_member(
            self,
            session: AsyncSession,
            user_fixture: User,
            schedule_fixture: CenterSchedule,
            schedule_member_fixture: CenterScheduleMember
    ):
        # then
        assert schedule_member_fixture.schedule.id == schedule_fixture.id
        assert schedule_member_fixture.user.id == user_fixture.id
