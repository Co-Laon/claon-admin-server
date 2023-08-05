from datetime import datetime
from typing import List

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.model.schedule import ScheduleRequestDto, ScheduleResponseDto, ScheduleInfoDto
from claon_admin.schema.center import Center, CenterScheduleMember, CenterSchedule
from claon_admin.schema.user import User
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for create schedule")
class TestCreateSchedule(object):
    @pytest.fixture
    async def schedule_create_request_dto(self, user_fixture: User):
        yield ScheduleRequestDto(
            member_list=[user_fixture.id],
            schedule_info=ScheduleInfoDto(
                title="title",
                start_time=datetime(2023, 1, 1, 10, 0),
                end_time=datetime(2023, 1, 2, 10, 0),
                description="description"
            )
        )

    @pytest.mark.asyncio
    @pytest.mark.it("Success case for creating center schedule")
    async def test_create_schedule(
            self,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center,
            new_schedule_fixture: CenterSchedule,
            new_schedule_member_fixture: List[CenterScheduleMember],
            schedule_create_request_dto: ScheduleRequestDto
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns="test@claon.com", role=Role.CENTER_ADMIN)

        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]
        mock_repo["center_schedule"].save.side_effect = [new_schedule_fixture]
        mock_repo["user"].find_by_ids.side_effect = [[user_fixture]]
        mock_repo["center_schedule_member"].save_all.side_effect = [new_schedule_member_fixture]

        response = ScheduleResponseDto.from_entity(new_schedule_fixture, [user_fixture])

        # when
        result = await center_service.create_schedule(request_user, center_fixture.id, schedule_create_request_dto)

        # then
        assert result == response

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: center is not exist')
    async def test_create_schedule_with_not_exist_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            schedule_create_request_dto: ScheduleRequestDto
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.create_schedule(request_user, "wrong_id", schedule_create_request_dto)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: user is not center owner')
    async def test_create_schedule_with_not_center_admin(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            schedule_create_request_dto: ScheduleRequestDto
    ):
        # given
        request_user = RequestUser(id="user_id", sns="test@claon.com", role=Role.USER)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.create_schedule(request_user, center_fixture.id, schedule_create_request_dto)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
