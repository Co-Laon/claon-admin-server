import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.schema.center import Center, CenterSchedule
from claon_admin.schema.user import User
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for delete center schedule")
class TestDeleteCenterSchedule(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_delete_center_schedule(
            self,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center,
            schedule_fixture: CenterSchedule
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns="sns@gmail.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["center_schedule"].find_by_id.side_effect = [schedule_fixture]
        mock_repo["center_schedule"].delete.side_effect = [schedule_fixture]

        # when
        result = await center_service.delete_schedule(request_user, center_fixture.id, schedule_fixture.id)

        # then
        assert result == schedule_fixture

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_delete_center_schedule_with_not_exist_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            schedule_fixture: CenterSchedule
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns="sns@gmail.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.delete_schedule(request_user, "wrong id", schedule_fixture.id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: user is not center owner")
    async def test_delete_center_schedule_with_not_center_owner(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            schedule_fixture: CenterSchedule
    ):
        # given
        request_user = RequestUser(id="not owner id", sns="sns@gmail.com", role=Role.USER)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.delete_schedule(request_user, center_fixture.id, schedule_fixture.id)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: schedule is not found")
    async def test_delete_center_schedule_with_not_exist_schedule(
            self,
            center_service: CenterService,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns="sns@gmail.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["center_schedule"].find_by_id.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.delete_schedule(request_user, center_fixture.id, "wrong id")

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST
