import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.center import Center, CenterHold
from tests.repository.center.conftest import center_hold_repository


@pytest.mark.describe("Test case for center hold repository")
class TestCenterHoldRepository(object):
    @pytest.mark.asyncio
    async def test_save_center_hold(
            self,
            session: AsyncSession,
            center_fixture: Center,
            center_holds_fixture: CenterHold
    ):
        assert center_holds_fixture.center == center_fixture
        assert center_holds_fixture.name == "hold_name"
        assert center_holds_fixture.difficulty == "hard"
        assert center_holds_fixture.is_color is False

    @pytest.mark.asyncio
    async def test_save_all_center_holds(
            self,
            session: AsyncSession,
            center_fixture: Center,
            center_holds_fixture: CenterHold
    ):
        # when
        center_holds = await center_hold_repository.save_all(session, [center_holds_fixture])

        # then
        assert center_holds == [center_holds_fixture]

    @pytest.mark.asyncio
    async def test_find_all_center_holds_by_center_id(
            self,
            session: AsyncSession,
            center_fixture: Center,
            center_holds_fixture: CenterHold
    ):
        # when
        center_holds = await center_hold_repository.find_all_by_center_id(session, center_fixture.id)

        # then
        assert center_holds == [center_holds_fixture]
