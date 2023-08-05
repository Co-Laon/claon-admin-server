from datetime import datetime

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.model.schedule import ScheduleRequestDto, ScheduleResponseDto, ScheduleInfoDto
from claon_admin.schema.center import Center, CenterSchedule, CenterScheduleMember
from claon_admin.schema.user import User
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for update schedule")
class TestUpdateSchedule(object):
    @pytest.fixture
    async def schedule_update_request_dto(self, client_user_fixture: User):
        yield ScheduleRequestDto(
            member_list=[client_user_fixture.id],
            schedule_info=ScheduleInfoDto(
                title="updated_title",
                start_time=datetime(2023, 10, 1, 10, 0),
                end_time=datetime(2023, 10, 2, 10, 0),
                description="updated_description"
            )
        )

    @pytest.mark.asyncio
    @pytest.mark.it("Success case for updating center schedule")
    async def test_update_schedule(
            self,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            client_user_fixture: User,
            center_fixture: Center,
            schedule_fixture: CenterSchedule,
            schedule_member_fixture: CenterScheduleMember,
            updated_schedule_member_fixture: CenterScheduleMember,
            schedule_update_request_dto: ScheduleRequestDto
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns="sns@gmail.com", role=Role.CENTER_ADMIN)

        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["center_schedule"].find_by_id_and_center_id.side_effect = [schedule_fixture]
        mock_repo["center_schedule_member"].delete_by_schedule_id.side_effect = [schedule_member_fixture]
        mock_repo["user"].find_by_id.side_effect = [client_user_fixture]
        mock_repo["center_schedule_member"].save.side_effect = [updated_schedule_member_fixture]

        schedule_fixture.update(**schedule_update_request_dto.schedule_info.dict())

        response = ScheduleResponseDto.from_entity(schedule_fixture, [client_user_fixture])

        # when
        result = await center_service.update_schedule(request_user,
                                                      center_fixture.id,
                                                      schedule_fixture.id,
                                                      schedule_update_request_dto)

        # then
        assert result == response

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: center is not found')
    async def test_update_schedule_with_not_found_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            schedule_fixture: CenterSchedule,
            schedule_update_request_dto: ScheduleRequestDto
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns="sns@gmail.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.update_schedule(request_user,
                                                 "wrong id",
                                                 schedule_fixture.id,
                                                 schedule_update_request_dto)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: request user is not center owner')
    async def test_update_schedule_with_not_center_owner(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            schedule_fixture: CenterSchedule,
            schedule_update_request_dto: ScheduleRequestDto
    ):
        # given
        request_user = RequestUser(id="010203", sns="sns@gmail.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.update_schedule(request_user,
                                                 center_fixture.id,
                                                 schedule_fixture.id,
                                                 schedule_update_request_dto)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: schedule is not found')
    async def test_update_schedule_with_not_found_schedule(
            self,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center,
            schedule_update_request_dto: ScheduleRequestDto
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns="sns@gmail.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["center_schedule"].find_by_id_and_center_id.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.update_schedule(request_user,
                                                 center_fixture.id,
                                                 "wrong id",
                                                 schedule_update_request_dto)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: exist wrong user in member list')
    async def test_update_schedule_with_not_found_user_in_member_list(
            self,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center,
            schedule_fixture: CenterSchedule,
            schedule_update_request_dto: ScheduleRequestDto
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns="sns@gmail.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["center_schedule"].find_by_id_and_center_id.side_effect = [schedule_fixture]
        mock_repo["user"].find_by_id.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.update_schedule(request_user,
                                                 center_fixture.id,
                                                 schedule_fixture.id,
                                                 schedule_update_request_dto)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST
