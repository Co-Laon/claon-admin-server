import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import UnauthorizedException, ErrorCode, BadRequestException
from claon_admin.model.auth import RequestUser
from claon_admin.schema.user import Lector
from claon_admin.service.admin import AdminService


@pytest.mark.describe("Test case for reject lector")
class TestRejectLector:
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_reject_lector(
            self,
            mock_repo: dict,
            admin_service: AdminService,
            lector_fixture: Lector
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
        lector_id = lector_fixture.id

        mock_repo["lector"].find_by_id.side_effect = [lector_fixture]
        mock_repo["lector"].delete.side_effect = [lector_fixture]

        # when
        result = await admin_service.reject_lector(None, request_user, lector_id)

        # then
        assert result is lector_fixture

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request user is not admin")
    async def test_reject_lector_with_non_admin(
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
            await admin_service.reject_lector(None, request_user, lector_id)

        # then
        assert exception.value.code == ErrorCode.NONE_ADMIN_ACCOUNT

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: lector is not found")
    async def test_reject_not_existing_lector(
            self,
            mock_repo: dict,
            admin_service: AdminService
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
        lector_id = "not_existing_id"

        mock_repo["lector"].find_by_id.side_effect = [None]

        with pytest.raises(BadRequestException) as exception:
            # when
            await admin_service.reject_lector(None, request_user, lector_id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST
