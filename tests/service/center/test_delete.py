from typing import List

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterResponseDto
from claon_admin.schema.center import Center, CenterFee, CenterHold, CenterWall
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for delete center")
class TestDelete(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_delete(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            center_fees_fixture: List[CenterFee],
            center_holds_fixture: List[CenterHold],
            center_walls_fixture: List[CenterWall]
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]
        response = CenterResponseDto.from_entity(entity=center_fixture,
                                                 holds=center_holds_fixture,
                                                 walls=center_walls_fixture,
                                                 fees=center_fees_fixture)

        # when
        result = await center_service.delete(subject=request_user, center_id=center_fixture.id)

        # then
        assert result.center_id == center_fixture.id
        assert result.fee_list == response.fee_list
        assert result.hold_info == response.hold_info
        assert result.wall_list == response.wall_list

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_delete_with_not_exist_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [None]
        wrong_id = "wrong id"

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.delete(subject=request_user, center_id=wrong_id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request user is not admin")
    async def test_delete_with_not_center_admin(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.delete(subject=request_user, center_id=center_fixture.id)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
