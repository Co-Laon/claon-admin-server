import pytest
from datetime import datetime
from claon_admin.common.enum import Role
from claon_admin.common.error.exception import ErrorCode, NotFoundException, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.schema.user import User
from claon_admin.model.schedule import ScheduleBriefResponseDto, ScheduleViewRequestDto
from claon_admin.schema.center import Center, CenterSchedule
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for find schedules by center")
class TestFindSchedulesByCenter(object):
    @pytest.fixture
    async def schedule_view_request_dto(self, user_fixture: User):
        yield ScheduleViewRequestDto(date_from="2023-07-30")

    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_find_schedule_by_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center,
            schedule_fixture: CenterSchedule,
            schedule_view_request_dto: ScheduleViewRequestDto
    ):
        # given
        request_user = RequestUser(id=center_fixture.user_id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["center_schedule"].find_by_center_id_and_date_from.return_value = [schedule_fixture]

        response = [ScheduleBriefResponseDto.from_entity(schedule_fixture)]

        # when
        result = await center_service.find_schedules_by_center(request_user, center_fixture.id, schedule_view_request_dto)

        # then
        assert response == result 

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_find_schedule_by_center_with_not_exist_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            schedule_view_request_dto: ScheduleViewRequestDto
    ):
        # given
        request_user = RequestUser(id=center_fixture.user_id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.find_schedules_by_center(request_user, center_fixture.id, schedule_view_request_dto)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: user is not center admin")
    async def test_find_schedule_by_center_without_center_admin(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            schedule_view_request_dto: ScheduleViewRequestDto
    ):
        # given
        request_user = RequestUser(id="0121212", sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.find_schedules_by_center(request_user, center_fixture.id, schedule_view_request_dto)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
