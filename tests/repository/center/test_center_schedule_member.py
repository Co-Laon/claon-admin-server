import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.center import CenterSchedule, CenterScheduleMember
from claon_admin.schema.user import User
from tests.repository.center.conftest import center_schedule_member_repository


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

    @pytest.mark.asyncio
    async def test_delete_schedule_member_by_schedule_id(
            self,
            session: AsyncSession,
            schedule_fixture: CenterSchedule,
            schedule_member_fixture: CenterScheduleMember
    ):
        # when
        await center_schedule_member_repository.delete_by_schedule_id(session, schedule_fixture.id)

        # then
        assert await center_schedule_member_repository.find_by_id(session, schedule_member_fixture.id) is None
