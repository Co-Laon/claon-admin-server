from typing import List

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import ErrorCode, NotFoundException, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterFeeDetailResponseDto
from claon_admin.schema.center import Center, CenterFee
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for find center fees")
class TestFindCenterFees(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_find_center_fees(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            center_fees_fixture: List[CenterFee]
    ):
        # given
        request_user = RequestUser(id=center_fixture.user_id, sns="test@google.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]
        response = CenterFeeDetailResponseDto.from_entity(center_fixture, center_fees_fixture)

        # when
        result = await center_service.find_center_fees(request_user, center_fixture.id)

        # then
        assert result == response
        assert result.center_fee[0].name == center_fees_fixture[0].name
        assert result.fee_img[0] == response.fee_img[0]

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: center is not found')
    async def test_find_center_fees_with_not_exist_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id=center_fixture.user_id, sns="test@google.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.find_center_fees(request_user, center_fixture.id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: request user is not center owner')
    async def test_find_center_fees_with_not_center_owner(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id="20230711", sns="test@google.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.find_center_fees(request_user, center_fixture.id)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
