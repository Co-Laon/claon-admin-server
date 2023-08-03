import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import ErrorCode, NotFoundException, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.schema.user import User
from claon_admin.model.schedule import ScheduleResponseDto
from claon_admin.schema.center import Center, CenterSchedule, CenterScheduleMember
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for find schedule detail by id")
class TestFindScheduleDetailByID(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_find_schedule_detail_by_id(
            self,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center,
            new_schedule_fixture: CenterSchedule,
            new_schedule_member_fixture: CenterScheduleMember
    ):
        # given
        request_user = RequestUser(id=center_fixture.user_id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["center_schedule"].find_by_id_and_center_id.side_effect = [new_schedule_fixture]

        response = ScheduleResponseDto.from_entity(new_schedule_fixture, [user_fixture])

        # when
        result = await center_service.find_schedule_detail_by_id(request_user, center_fixture.id, new_schedule_fixture.id)

        # then
        assert response == result 

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_find_schedule_detail_by_id_with_not_exist_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            new_schedule_fixture: CenterSchedule
    ):
        # given
        request_user = RequestUser(id=center_fixture.user_id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.find_schedule_detail_by_id(request_user, center_fixture.id, new_schedule_fixture.id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: schedule is not found")
    async def test_find_schedule_detail_by_id_with_not_exist_schedule(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            new_schedule_fixture: CenterSchedule
    ):
        # given
        request_user = RequestUser(id=center_fixture.user_id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["center_schedule"].find_by_id_and_center_id.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.find_schedule_detail_by_id(request_user, center_fixture.id, new_schedule_fixture.id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: user is not center admin")
    async def test_find_schedule_detail_by_id_without_center_admin(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            new_schedule_fixture: CenterSchedule
    ):
        # given
        request_user = RequestUser(id="0121212", sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.find_schedule_detail_by_id(request_user, center_fixture.id, new_schedule_fixture.id)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
    