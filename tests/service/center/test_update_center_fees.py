from typing import List

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterFeeDetailResponseDto, CenterFeeDetailRequestDto, CenterFeeRequestDto
from claon_admin.schema.center import Center, CenterFee
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for update center fees")
class TestUpdateCenterFees(object):
    @pytest.fixture
    async def center_fee_detail_request_dto(self, center_fees_fixture: List[CenterFee], new_center_fees_fixture: CenterFee):
        yield CenterFeeDetailRequestDto(
            fee_img=['https://test.fee.png'],
            center_fee=[
                CenterFeeRequestDto(
                    center_fee_id=center_fees_fixture[0].id,
                    name=center_fees_fixture[0].name,
                    fee_type=center_fees_fixture[0].fee_type,
                    price=center_fees_fixture[0].price,
                    count=center_fees_fixture[0].count,
                    period=center_fees_fixture[0].period,
                    period_type=center_fees_fixture[0].period_type
                ),
                CenterFeeRequestDto(
                    name=new_center_fees_fixture.name,
                    fee_type=new_center_fees_fixture.fee_type,
                    price=new_center_fees_fixture.price,
                    count=new_center_fees_fixture.count,
                    period=new_center_fees_fixture.period,
                    period_type=new_center_fees_fixture.period_type
                )
            ]
        )

    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_update_center_fees(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            center_fees_fixture: List[CenterFee],
            new_center_fees_fixture: CenterFee,
            center_fee_detail_request_dto: CenterFeeDetailRequestDto
    ):
        # given
        center_fixture.fees = center_fees_fixture
        request_user = RequestUser(id=center_fixture.user_id, sns="test@craon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]
        mock_repo["center_fee"].save.side_effect = [new_center_fees_fixture]

        response = CenterFeeDetailResponseDto.from_entity(center_fixture, [center_fees_fixture[0], new_center_fees_fixture])

        # when
        result = await center_service.update_center_fees(request_user, center_fixture.id, center_fee_detail_request_dto)

        # then
        assert result == response

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
            await center_service.update_center_fees(request_user, "wrong id", center_fee_detail_request_dto)

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
            await center_service.update_center_fees(request_user, center_fixture.id, center_fee_detail_request_dto)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
