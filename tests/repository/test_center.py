import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.model.enum import WallType, Role
from claon_admin.schema.center import (
    CenterRepository,
    CenterApprovedFileRepository, CenterHoldRepository, CenterWallRepository, Center, CenterHold, CenterWall,
    CenterApprovedFile
)
from claon_admin.schema.user import User, UserRepository

user_repository = UserRepository()
center_repository = CenterRepository()
center_approved_file_repository = CenterApprovedFileRepository()
center_hold_repository = CenterHoldRepository()
center_wall_repository = CenterWallRepository()


@pytest.mark.asyncio
async def test_save_center(
        session: AsyncSession,
        user_fixture,
        center_fixture
):
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
    assert center_fixture.approved is False


@pytest.mark.asyncio
async def test_find_center_by_id(
        session: AsyncSession,
        center_fixture: Center
):
    # given
    center_id = center_fixture.id

    # when
    result = await center_repository.find_by_id(session, center_id)

    # then
    assert result == center_fixture


@pytest.mark.asyncio
async def test_find_center_by_non_existing_id(
        session: AsyncSession
):
    # given
    center_id = "non_existing_id"

    # when
    result = await center_repository.find_by_id(session, center_id)

    # then
    assert result is None


@pytest.mark.asyncio
async def test_exists_center_by_id(
        session: AsyncSession,
        center_fixture: Center
):
    # given
    center_id = center_fixture.id

    # when
    result = await center_repository.exists_by_id(session, center_id)

    # then
    assert result


@pytest.mark.asyncio
async def test_exists_center_by_non_existing_id(
        session: AsyncSession
):
    # given
    center_id = "non_existing_id"

    # when
    result = await center_repository.exists_by_id(session, center_id)

    # then
    assert result is False


@pytest.mark.asyncio
async def test_approve_center(
        session: AsyncSession,
        center_fixture: Center
):
    # when
    result = await center_repository.approve(session, center_fixture)

    # then
    assert result.approved
    assert result.user.role == Role.CENTER_ADMIN


@pytest.mark.asyncio
async def test_delete_center(
        session: AsyncSession,
        center_fixture: Center
):
    # when
    await center_repository.delete(session, center_fixture)

    # then
    assert await center_repository.find_by_id(session, center_fixture.id) is None
    assert await center_hold_repository.find_all_by_center_id(session, center_fixture.id) == []
    assert await center_wall_repository.find_all_by_center_id(session, center_fixture.id) == []
    assert await center_approved_file_repository.find_all_by_center_id(session, center_fixture.id) == []


@pytest.mark.asyncio
async def test_save_center_approved_files(
        session: AsyncSession,
        user_fixture,
        center_fixture,
        center_approved_file_fixture
):
    # then
    assert center_approved_file_fixture.center == center_fixture
    assert center_approved_file_fixture.center_id == center_fixture.id
    assert center_approved_file_fixture.user == user_fixture
    assert center_approved_file_fixture.user_id == user_fixture.id
    assert center_approved_file_fixture.url == "https://example.com/approved.jpg"


@pytest.mark.asyncio
async def test_save_all_center_approved_files(
        session: AsyncSession,
        user_fixture: User,
        center_fixture: Center,
        center_approved_file_fixture
):
    # when
    center_approved_files = await center_approved_file_repository.save_all(session, [center_approved_file_fixture])

    # then
    assert center_approved_files == [center_approved_file_fixture]


@pytest.mark.asyncio
async def test_find_all_center_approved_files_by_center_id(
        session: AsyncSession,
        center_fixture: Center,
        center_approved_file_fixture: CenterApprovedFile
):
    # when
    center_approved_files = await center_approved_file_repository.find_all_by_center_id(session, center_fixture.id)

    # then
    assert center_approved_files == [center_approved_file_fixture]


@pytest.mark.asyncio
async def test_save_center_hold(
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
        session: AsyncSession,
        center_fixture: Center,
        center_holds_fixture: CenterHold
):
    # when
    center_holds = await center_hold_repository.find_all_by_center_id(session, center_fixture.id)

    # then
    assert center_holds == [center_holds_fixture]


@pytest.mark.asyncio
async def test_save_center_wall(
        session: AsyncSession,
        center_fixture: Center,
        center_walls_fixture: CenterWall
):
    assert center_walls_fixture.center == center_fixture
    assert center_walls_fixture.name == "wall"
    assert center_walls_fixture.type == WallType.ENDURANCE.value


@pytest.mark.asyncio
async def test_save_all_center_walls(
        session: AsyncSession,
        center_fixture: Center,
        center_walls_fixture: CenterWall
):
    # when
    center_walls = await center_hold_repository.save_all(session, [center_walls_fixture])

    # then
    assert center_walls == [center_walls_fixture]


@pytest.mark.asyncio
async def test_find_all_center_walls_by_center_id(
        session: AsyncSession,
        center_fixture: Center,
        center_walls_fixture: CenterWall
):
    # when
    center_walls = await center_wall_repository.find_all_by_center_id(session, center_fixture.id)

    # then
    assert center_walls == [center_walls_fixture]
