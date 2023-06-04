from typing import List

import pytest

from claon_admin.common.error.exception import NotFoundException, ErrorCode
from claon_admin.model.center import CenterResponseDto
from claon_admin.schema.center import Center, CenterFee, CenterHold, CenterWall
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for delete review answer")
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
        response = CenterResponseDto.from_entity(center_fixture, center_holds_fixture, center_walls_fixture, center_fees_fixture)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]

        # when
        result = await center_service.delete(None, center_fixture.id)

        # then
        assert result.center_id == center_fixture.id
        assert result.fee_list == response.fee_list
        assert result.hold_list == response.hold_list
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
        mock_repo["center"].find_by_id.side_effect = [None]
        wrong_id = "wrong id"

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.delete(None, wrong_id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST
