import pytest

from claon_admin.model.center import CenterNameResponseDto
from claon_admin.schema.center import Center
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for find centers by name")
class TestFindCentersByName(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_find_centers_by_name(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center
    ):
        # given
        response = CenterNameResponseDto.from_entity(center_fixture)
        mock_repo["center"].find_by_name.side_effect = [[center_fixture]]

        # when
        result = await center_service.find_centers_by_name(center_fixture.name)

        # then
        assert len(result) == 1
        assert response in result
