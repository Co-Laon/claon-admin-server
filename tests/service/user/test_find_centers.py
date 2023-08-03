import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import ErrorCode, NotFoundException
from claon_admin.model.auth import RequestUser
from claon_admin.model.user import CenterNameResponseDto

from claon_admin.schema.center import Center
from claon_admin.schema.user import User
from claon_admin.service.user import UserService


@pytest.mark.describe("Test case for find centers")
class TestFindCenters(object):

    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_find_centers(
            self,
            user_service: UserService,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center,
            other_center_fixture: Center
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        result_center = [center_fixture, other_center_fixture]
        mock_repo["center"].find_by_user_id.side_effect = [result_center]
        response = [CenterNameResponseDto.from_entity(entity=e) for e in result_center]

        # when
        result = await user_service.find_centers(request_user)

        # then
        assert result == response

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: not found centers")
    async def test_find_centers_with_not_centers(
            self,
            user_service: UserService,
            mock_repo: dict,
            user_fixture: User
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_user_id.side_effect = [[]]

        with pytest.raises(NotFoundException) as exception:
            # when
            await user_service.find_centers(request_user)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST
