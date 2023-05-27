import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.center import Center, CenterApprovedFile
from claon_admin.schema.user import User
from tests.repository.center.conftest import center_approved_file_repository


@pytest.mark.describe("Test case for center approved file repository")
class TestCenterApprovedFileRepository(object):
    @pytest.mark.asyncio
    async def test_save_center_approved_file(
            self,
            session: AsyncSession,
            user_fixture: User,
            center_fixture: Center,
            center_approved_file_fixture: CenterApprovedFile
    ):
        # then
        assert center_approved_file_fixture.center == center_fixture
        assert center_approved_file_fixture.center_id == center_fixture.id
        assert center_approved_file_fixture.user == user_fixture
        assert center_approved_file_fixture.user_id == user_fixture.id
        assert center_approved_file_fixture.url == "https://example.com/approved.jpg"

    @pytest.mark.asyncio
    async def test_save_all_center_approved_files(
            self,
            session: AsyncSession,
            user_fixture: User,
            center_fixture: Center,
            center_approved_file_fixture: CenterApprovedFile
    ):
        # when
        center_approved_files = await center_approved_file_repository.save_all(session, [center_approved_file_fixture])

        # then
        assert center_approved_files == [center_approved_file_fixture]

    @pytest.mark.asyncio
    async def test_find_all_center_approved_files_by_center_id(
            self,
            session: AsyncSession,
            center_fixture: Center,
            center_approved_file_fixture: CenterApprovedFile
    ):
        # when
        center_approved_files = await center_approved_file_repository.find_all_by_center_id(session, center_fixture.id)

        # then
        assert center_approved_files == [center_approved_file_fixture]

    @pytest.mark.asyncio
    async def test_delete_all_center_approved_files_by_center_id(
            self,
            session: AsyncSession,
            center_fixture: Center
    ):
        # when
        await center_approved_file_repository.delete_all_by_center_id(session, center_fixture.id)

        # then
        assert await center_approved_file_repository.find_all_by_center_id(session, center_fixture.id) == []
