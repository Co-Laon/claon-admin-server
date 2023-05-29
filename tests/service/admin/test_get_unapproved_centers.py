from typing import List

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import UnauthorizedException, ErrorCode
from claon_admin.model.admin import CenterResponseDto
from claon_admin.model.auth import RequestUser
from claon_admin.schema.center import Center, CenterApprovedFile
from claon_admin.service.admin import AdminService


@pytest.mark.describe("Test case for get unapproved centers")
class TestGetUnapprovedCenters(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_get_unapproved_centers(
            self,
            mock_repo: dict,
            admin_service: AdminService,
            center_fixture: Center,
            center_approved_files_fixture: List[CenterApprovedFile]
    ):
        # given
        response = CenterResponseDto.from_entity(center_fixture, center_approved_files_fixture)
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
        mock_repo["center"].find_all_by_approved_false.side_effect = [[center_fixture]]
        mock_repo["center_approved_file"].find_all_by_center_id.side_effect = [center_approved_files_fixture]

        # when
        result: List[CenterResponseDto] = await admin_service.get_unapproved_centers(None, request_user)

        # then
        assert len(result) == 1
        assert mock_repo["center"].find_all_by_approved_false.call_count == len(result)

        for center in result:
            assert center == response

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request user is not admin")
    async def test_get_unapproved_centers_with_non_admin(
            self,
            mock_repo: dict,
            admin_service: AdminService,
            center_fixture: Center,
            center_approved_files_fixture: List[CenterApprovedFile]
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
        mock_repo["center"].find_all_by_approved_false.side_effect = [[center_fixture]]
        mock_repo["center_approved_file"].find_all_by_center_id.side_effect = [center_approved_files_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await admin_service.get_unapproved_centers(None, request_user)

        # then
        assert exception.value.code == ErrorCode.NONE_ADMIN_ACCOUNT
