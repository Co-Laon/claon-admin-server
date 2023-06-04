from typing import List

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import UnauthorizedException, ErrorCode
from claon_admin.model.admin import LectorResponseDto
from claon_admin.model.auth import RequestUser
from claon_admin.schema.user import Lector, LectorApprovedFile
from claon_admin.service.admin import AdminService


@pytest.mark.describe("Test case for get unapproved lectors")
class TestGetUnapprovedLectors(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_get_unapproved_lectors(
            self,
            mock_repo: dict,
            admin_service: AdminService,
            lector_fixture: Lector,
            lector_approved_files_fixture: List[LectorApprovedFile]
    ):
        # given
        response = LectorResponseDto.from_entity(lector_fixture, lector_approved_files_fixture)
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
        mock_repo["lector"].find_all_by_approved_false.side_effect = [[lector_fixture]]
        mock_repo["lector_approved_file"].find_all_by_lector_id.side_effect = [lector_approved_files_fixture]

        # when
        result: List[LectorResponseDto] = await admin_service.get_unapproved_lectors(request_user)

        # then
        assert len(result) == 1
        assert mock_repo["lector"].find_all_by_approved_false.call_count == len(result)

        for lector in result:
            assert lector == response

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request user is not admin")
    async def test_get_unapproved_lectors_with_non_admin(
            self,
            mock_repo: dict,
            admin_service: AdminService,
            lector_fixture: Lector,
            lector_approved_files_fixture: List[LectorApprovedFile]
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
        mock_repo["lector"].find_all_by_approved_false.side_effect = [[lector_fixture]]
        mock_repo["lector_approved_file"].find_all_by_lector_id.side_effect = [lector_approved_files_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await admin_service.get_unapproved_lectors(request_user)

        # then
        assert exception.value.code == ErrorCode.NONE_ADMIN_ACCOUNT
