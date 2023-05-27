from typing import List
from unittest.mock import patch

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import UnauthorizedException, ErrorCode, BadRequestException
from claon_admin.model.auth import RequestUser
from claon_admin.schema.user import Lector, LectorApprovedFile
from claon_admin.service.admin import AdminService


@pytest.mark.describe("Test case for approve lector")
class TestApproveLector(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    @patch("claon_admin.service.admin.delete_file")
    async def test_approve_lector(
            self,
            mock_delete_file,
            mock_repo: dict,
            admin_service: AdminService,
            lector_fixture: Lector,
            lector_approved_files_fixture: List[LectorApprovedFile]
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
        lector_id = lector_fixture.id

        mock_repo["lector"].find_by_id.side_effect = [lector_fixture]
        lector_fixture.approved = True
        mock_repo["lector"].approve.side_effect = [lector_fixture]
        lector_fixture.user.role = Role.LECTOR
        mock_repo["user"].update_role.side_effect = [lector_fixture.user]
        mock_repo["lector_approved_file"].find_all_by_lector_id.side_effect = [lector_approved_files_fixture]

        # when
        result = await admin_service.approve_lector(None, request_user, lector_id)

        # then
        assert result.approved
        assert result.user_profile.role == Role.LECTOR

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request user is not admin")
    async def test_approve_lector_with_non_admin(
            self,
            mock_repo: dict,
            admin_service: AdminService,
            lector_fixture: Lector
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
        lector_id = lector_fixture.id

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await admin_service.approve_lector(None, request_user, lector_id)

        # then
        assert exception.value.code == ErrorCode.NONE_ADMIN_ACCOUNT

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: lector is not found")
    async def test_approve_not_existing_lector(
            self,
            mock_repo: dict,
            admin_service: AdminService,
            lector_fixture: Lector
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
        lector_id = "not_existing_id"

        mock_repo["lector"].find_by_id.side_effect = [None]

        with pytest.raises(BadRequestException) as exception:
            # when
            await admin_service.approve_lector(None, request_user, lector_id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST
