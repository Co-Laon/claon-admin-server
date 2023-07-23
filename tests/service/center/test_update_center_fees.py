from typing import List

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterFeeDetailResponseDto, CenterFeeDetailRequestDto, CenterFeeResponseDto
from claon_admin.schema.center import Center, CenterFee
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for update center fees")
class TestUpdateCenterFees(object):
    @pytest.fixture
    async def center_fee_detail_request_dto(self, center_fixture):
        yield CenterFeeDetailRequestDto(
            fee_img=[e.url for e in center_fixture.fee_img],
            center_fee=[CenterFeeResponseDto(
                center_fee_id=e.id,
                name=e.name,
                fee_type=e.fee_type,
                price=e.price,
                count=e.count,
                period=e.period,
                period_type=e.period_type
            ) for e in center_fixture.fees]
        )

    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_update_center_fees(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            center_fees_fixture: List[CenterFee],
            center_fee_detail_request_dto: CenterFeeDetailRequestDto
    ):
        # given
        center_fixture.fees = center_fees_fixture
        request_user = RequestUser(id=center_fixture.user_id, sns="test@craon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]
        mock_repo["center_fee"].save_all.side_effect = [center_fees_fixture]

        response = CenterFeeDetailResponseDto.from_entity(entity=center_fixture, fees=center_fees_fixture)

        # when
        result = await center_service.update_center_fees(subject=request_user, 
                                                         center_id=center_fixture.id, 
                                                         dto=center_fee_detail_request_dto)

        # then
        assert result == response
        assert result.center_fee[0].name == center_fees_fixture[0].name
        assert result.fee_img[0] == response.fee_img[0]
    
    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: center is not found')
    async def test_update_with_not_exist_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            center_fee_detail_request_dto: CenterFeeDetailRequestDto
        ):
        # given
        request_user = RequestUser(id=center_fixture.user_id, sns="test@craon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.update_center_fees(center_id="wrong id", subject=request_user, 
                                        dto=center_fee_detail_request_dto)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: request user is not center admin')
    async def test_update_with_not_center_admin(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            center_fee_detail_request_dto: CenterFeeDetailRequestDto            
        ):
        # given
        request_user = RequestUser(id="0123123", sns="test@craon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.update_center_fees(center_id=center_fixture.id, subject=request_user,
                                        dto=center_fee_detail_request_dto)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
