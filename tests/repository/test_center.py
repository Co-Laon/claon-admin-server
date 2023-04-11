import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.model.enum import WallType
from claon_admin.schema.center import CenterRepository

center_repository = CenterRepository()


@pytest.mark.asyncio
async def test_save(session: AsyncSession, user_fixture, center_fixture):
    # then
    assert center_fixture.user.id == user_fixture.id
    assert center_fixture.user == user_fixture
    assert center_fixture.name == "test center"
    assert center_fixture.profile_img == "https://test.profile.png"
    assert center_fixture.address == "test_address"
    assert center_fixture.detail_address == "test_detail_address"
    assert center_fixture.tel == "010-1234-5678"
    assert center_fixture.web_url == "http://test.com"
    assert center_fixture.instagram_name == "test_instagram"
    assert center_fixture.youtube_url == "https://www.youtube.com/@test"
    assert center_fixture.center_img[0].url == "https://test.image.png"
    assert center_fixture.operating_time[0].day_of_week == "월"
    assert center_fixture.operating_time[0].start_time == "09:00"
    assert center_fixture.operating_time[0].end_time == "18:00"
    assert center_fixture.utility[0].name == "test_utility"
    assert center_fixture.fee[0].name == "test_fee_name"
    assert center_fixture.fee[0].price == 1000
    assert center_fixture.fee[0].count == 10
    assert center_fixture.fee_img[0].url == "https://test.fee.png"
    assert center_fixture.holds[0].name == "test_hold"
    assert center_fixture.holds[0].difficulty == "#ffffff"
    assert center_fixture.holds[0].is_color
    assert center_fixture.walls[0].name == "test_wall"
    assert center_fixture.walls[0].type == WallType.ENDURANCE.value
    assert center_fixture.approved_files[0].url == "https://test.proof.png"
    assert center_fixture.approved is False
