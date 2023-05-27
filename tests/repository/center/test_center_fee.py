import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import MembershipType, PeriodType
from claon_admin.schema.center import Center, CenterFee
from tests.repository.center.conftest import center_fee_repository


@pytest.mark.describe("Test case for center fee repository")
class TestCenterFeeRepository(object):
    @pytest.mark.asyncio
    async def test_save_center_fee(
            self,
            session: AsyncSession,
            center_fixture: Center,
            center_fee_fixture: CenterFee
    ):
        assert center_fee_fixture.center == center_fixture
        assert center_fee_fixture.name == "fee_name"
        assert center_fee_fixture.membership_type == MembershipType.PACKAGE
        assert center_fee_fixture.price == 1000
        assert center_fee_fixture.count == 2
        assert center_fee_fixture.period == 2
        assert center_fee_fixture.period_type == PeriodType.MONTH

    @pytest.mark.asyncio
    async def test_save_all_center_fees(
            self,
            session: AsyncSession,
            center_fixture: Center,
            center_fee_fixture: CenterFee
    ):
        # when
        center_fees = await center_fee_repository.save_all(session, [center_fee_fixture])

        # then
        assert center_fees == [center_fee_fixture]

    @pytest.mark.asyncio
    async def test_find_all_center_fees_by_center_id(
            self,
            session: AsyncSession,
            center_fixture: Center,
            center_fee_fixture: CenterFee
    ):
        # when
        center_fees = await center_fee_repository.find_all_by_center_id(session, center_fixture.id)

        # then
        assert center_fees == [center_fee_fixture]
