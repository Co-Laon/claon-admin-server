from typing import List

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException, BadRequestException
from claon_admin.model.auth import RequestUser
from claon_admin.schema.center import CenterFee, Center
from claon_admin.schema.user import User
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for delete center fee")
class TestDeleteCenterFee(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_delete_center_fee(
            self,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center,
            center_fees_fixture: List[CenterFee],
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns=user_fixture.sns, role=user_fixture.role)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]

        # when
        result = await center_service.delete_center_fee(
            subject=request_user,
            center_id=center_fixture.id,
            center_fee_id=center_fees_fixture[0].id
        )

        # then
        assert result.is_deleted is True

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_delete_center_fee_with_not_exist_center(
            self,
            mock_repo: dict,
            user_fixture: User,
            center_fees_fixture: List[CenterFee],
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns=user_fixture.sns, role=user_fixture.role)
        mock_repo["center"].find_by_id_with_details.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.delete_center_fee(
                subject=request_user,
                center_id="wrong id",
                center_fee_id=center_fees_fixture[0].id
            )

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: user is not owner")
    async def test_delete_center_fee_with_not_center_owner(
            self,
            mock_repo: dict,
            center_fixture: Center,
            center_fees_fixture: List[CenterFee],
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id="not owner", sns="notowner@gmail.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.delete_center_fee(
                subject=request_user,
                center_id=center_fixture.id,
                center_fee_id=center_fees_fixture[0].id
            )

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center fee is not found")
    async def test_delete_center_fee_with_not_exist_center_fee(
            self,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center,
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns=user_fixture.sns, role=user_fixture.role)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.delete_center_fee(
                subject=request_user,
                center_id=center_fixture.id,
                center_fee_id="wrong id"
            )

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center fee is deleted")
    async def test_delete_center_fee_with_issued_center_fee(
            self,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center,
            center_fees_fixture: List[CenterFee],
            center_service: CenterService
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns=user_fixture.sns, role=user_fixture.role)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]

        with pytest.raises(BadRequestException) as exception:
            # when
            await center_service.delete_center_fee(
                subject=request_user,
                center_id=center_fixture.id,
                center_fee_id=center_fees_fixture[1].id
            )

        # then
        assert exception.value.code == ErrorCode.ROW_ALREADY_DETELED
