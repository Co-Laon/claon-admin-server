from unittest.mock import patch

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import ErrorCode, BadRequestException
from claon_admin.schema.user import Lector
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
            lector_fixture: Lector
    ):
        # given
        lector_id = lector_fixture.id

        mock_repo["lector"].find_by_id_with_user.side_effect = [lector_fixture]
        mock_repo["lector_approved_file"].find_all_by_lector_id.side_effect = [[]]
        mock_delete_file.return_value = None

        # when
        result = await admin_service.approve_lector(lector_id)

        # then
        assert result.approved
        assert result.user_profile.role == Role.LECTOR

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: lector is not found")
    async def test_approve_not_existing_lector(
            self,
            mock_repo: dict,
            admin_service: AdminService,
            lector_fixture: Lector
    ):
        # given
        lector_id = "not_existing_id"

        mock_repo["lector"].find_by_id_with_user.side_effect = [None]

        with pytest.raises(BadRequestException) as exception:
            # when
            await admin_service.approve_lector(lector_id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST
