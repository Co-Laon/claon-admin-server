import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import WallType
from claon_admin.schema.center import Center, CenterWall
from tests.repository.center.conftest import center_wall_repository


@pytest.mark.describe("Test case for center wall repository")
class TestCenterWallRepository(object):
    @pytest.mark.asyncio
    async def test_save_center_wall(
            self,
            session: AsyncSession,
            center_fixture: Center,
            center_walls_fixture: CenterWall
    ):
        assert center_walls_fixture.center == center_fixture
        assert center_walls_fixture.name == "wall"
        assert center_walls_fixture.type == WallType.ENDURANCE.value

    @pytest.mark.asyncio
    async def test_save_all_center_walls(
            self,
            session: AsyncSession,
            center_fixture: Center,
            center_walls_fixture: CenterWall
    ):
        # when
        center_walls = await center_wall_repository.save_all(session, [center_walls_fixture])

        # then
        assert center_walls == [center_walls_fixture]

    @pytest.mark.asyncio
    async def test_find_all_center_walls_by_center_id(
            self,
            session: AsyncSession,
            center_fixture: Center,
            center_walls_fixture: CenterWall
    ):
        # when
        center_walls = await center_wall_repository.find_all_by_center_id(session, center_fixture.id)

        # then
        assert center_walls == [center_walls_fixture]
