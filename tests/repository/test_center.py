import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.user import User, UserRepository
from claon_admin.schema.center import (
    Center,
    CenterRepository,
    CenterImage,
    OperatingTime,
    Utility,
    CenterFee,
    CenterFeeImage,
    CenterHold,
    CenterWall,
    CenterApprovedFile,
    CenterApprovedFileRepository
)

user_repository = UserRepository()
center_repository = CenterRepository()
center_approved_file_repository = CenterApprovedFileRepository()


@pytest.fixture(scope="session")
async def center_fixture(session: AsyncSession, user_fixture: User):
    center = Center(
        user=user_fixture,
        name="Test Center",
        profile_img="https://example.com/image.jpg",
        address="Test Address",
        detail_address="Test Detail Address",
        tel="Test Tel",
        web_url="https://example.com",
        instagram_name="Test Instagram",
        youtube_url="https://example.com"
    )

    center.center_img = CenterImage(url="https://example.com/image.jpg")
    center.operating_time = OperatingTime(day_of_week="Monday", start_time="09:00", end_time="18:00")
    center.utility = Utility(name="Test Utility")
    center.fee = CenterFee(price=1000, count=10)
    center.fee_img = CenterFeeImage(url="https://example.com/image.jpg")
    center_hold = CenterHold(name="Test Hold", color="#ffffff")
    center.holds.append(center_hold)
    center_wall = CenterWall(name="Test Wall", type="Test Type")
    center.walls.append(center_wall)

    center = await center_repository.save(session, center)
    yield center


@pytest.fixture(scope="session")
async def center_approved_files_fixture(session: AsyncSession, user_fixture: User, center_fixture: Center):
    center_approved_files = CenterApprovedFile(
        url="https://example.com/approved.jpg"
    )
    center_approved_files.user = user_fixture
    center_approved_files.center = center_fixture

    center_approved_files = await center_approved_file_repository.save(session, center_approved_files)
    yield center_approved_files


@pytest.mark.asyncio
async def test_save(session: AsyncSession, user_fixture: User, center_fixture: Center):
    # then
    assert center_fixture.name == "Test Center"
    assert center_fixture.profile_img == "https://example.com/image.jpg"
    assert center_fixture.address == "Test Address"
    assert center_fixture.detail_address == "Test Detail Address"
    assert center_fixture.tel == "Test Tel"
    assert center_fixture.web_url == "https://example.com"
    assert center_fixture.instagram_name == "Test Instagram"
    assert center_fixture.youtube_url == "https://example.com"
    assert center_fixture.center_img.url == "https://example.com/image.jpg"
    assert center_fixture.operating_time.day_of_week == "Monday"
    assert center_fixture.operating_time.start_time == "09:00"
    assert center_fixture.operating_time.end_time == "18:00"
    assert center_fixture.utility.name == "Test Utility"
    assert center_fixture.fee.price == 1000
    assert center_fixture.fee.count == 10
    assert center_fixture.fee_img.url == "https://example.com/image.jpg"
    assert center_fixture.holds[0].name == "Test Hold"
    assert center_fixture.holds[0].color == "#ffffff"
    assert center_fixture.walls[0].name == "Test Wall"
    assert center_fixture.walls[0].type == "Test Type"


@pytest.mark.asyncio
async def test_save_for_center_approved_files(
        session: AsyncSession,
        user_fixture: User,
        center_fixture: Center,
        center_approved_files_fixture: CenterApprovedFile):
    # then
    assert center_approved_files_fixture.center == center_fixture
    assert center_approved_files_fixture.center_id == center_fixture.id
    assert center_approved_files_fixture.user == user_fixture
    assert center_approved_files_fixture.user_id == user_fixture.id
    assert center_approved_files_fixture.url == "https://example.com/approved.jpg"
