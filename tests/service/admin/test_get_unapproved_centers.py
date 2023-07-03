from typing import List

import pytest

from claon_admin.model.admin import CenterResponseDto
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
        mock_repo["center"].find_all_by_approved_false.side_effect = [[center_fixture]]
        mock_repo["center_approved_file"].find_all_by_center_id.side_effect = [center_approved_files_fixture]

        # when
        result: List[CenterResponseDto] = await admin_service.get_unapproved_centers()

        # then
        assert len(result) == 1
        assert mock_repo["center"].find_all_by_approved_false.call_count == len(result)

        for center in result:
            assert center == response
