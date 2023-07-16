import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import UnauthorizedException, ErrorCode
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
        request_user = RequestUser(id=user_fixture.id, sns="test@claon.com", role=Role.LECTOR)
        result_center = [center_fixture, other_center_fixture]
        mock_repo["center"].find_by_user_id.side_effect = [result_center]
        response = [CenterNameResponseDto.from_entity(entity=e) for e in result_center]

        # when
        result = await user_service.find_centers(subject=request_user)

        # then
        assert result == response
