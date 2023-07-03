from typing import List

import pytest

from claon_admin.model.admin import LectorResponseDto
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
        mock_repo["lector"].find_all_by_approved_false.side_effect = [[lector_fixture]]
        mock_repo["lector_approved_file"].find_all_by_lector_id.side_effect = [lector_approved_files_fixture]

        # when
        result: List[LectorResponseDto] = await admin_service.get_unapproved_lectors()

        # then
        assert len(result) == 1
        assert mock_repo["lector"].find_all_by_approved_false.call_count == len(result)

        for lector in result:
            assert lector == response
