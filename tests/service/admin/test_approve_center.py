from typing import List
from unittest.mock import patch

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import UnauthorizedException, ErrorCode, BadRequestException, NotFoundException
from claon_admin.model.auth import RequestUser
from claon_admin.schema.center import Center, CenterApprovedFile
from claon_admin.service.admin import AdminService


@pytest.mark.describe("Test case for approve center")
class TestApproveCenter(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    @patch("claon_admin.service.admin.delete_file")
    async def test_success(
            self,
            mock_delete_file,
            mock_repo: dict,
            admin_service: AdminService,
            center_fixture: Center,
            center_approved_files_fixture: List[CenterApprovedFile]
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
        center_id = center_fixture.id

        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]
        center_fixture.approved = True
        mock_repo["center"].approve.side_effect = [center_fixture]
        mock_repo["center"].exists_by_name_and_approved.side_effect = [False]
        center_fixture.user.role = Role.CENTER_ADMIN
        mock_repo["user"].update_role.side_effect = [center_fixture.user]
        mock_repo["center_approved_file"].find_all_by_center_id.side_effect = [center_approved_files_fixture]

        # when
        result = await admin_service.approve_center(request_user, center_id)

        # then
        assert result.approved
        assert result.user_profile.role == Role.CENTER_ADMIN

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request user is not admin")
    async def test_approve_center_with_non_admin(
            self,
            mock_repo: dict,
            admin_service: AdminService,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
        center_id = center_fixture.id

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await admin_service.approve_center(request_user, center_id)

        # then
        assert exception.value.code == ErrorCode.NONE_ADMIN_ACCOUNT

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_approve_not_existing_center(
            self,
            mock_repo: dict,
            admin_service: AdminService
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
        center_id = "not_existing_id"

        mock_repo["center"].find_by_id_with_details.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await admin_service.approve_center(request_user, center_id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center name is duplicated")
    async def test_approve_duplicated_center_name(
            self,
            mock_repo: dict,
            admin_service: AdminService,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
        center_id = center_fixture.id

        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]
        mock_repo["center"].exists_by_name_and_approved.side_effect = [True]

        with pytest.raises(BadRequestException) as exception:
            # when
            await admin_service.approve_center(request_user, center_id)

        # then
        assert exception.value.code == ErrorCode.DUPLICATED_NICKNAME
