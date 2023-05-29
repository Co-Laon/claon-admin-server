import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.user import Lector, LectorApprovedFile
from tests.repository.user.conftest import lector_approved_file_repository


@pytest.mark.describe("Test case for lector approved file repository")
class TestLectorApprovedFileRepository(object):
    @pytest.mark.asyncio
    async def test_save_lector_approved_file(
            self,
            session: AsyncSession,
            lector_fixture: Lector,
            lector_approved_file_fixture: LectorApprovedFile
    ):
        # then
        assert lector_approved_file_fixture.lector == lector_fixture
        assert lector_approved_file_fixture.url == "https://test.com/test.pdf"

    @pytest.mark.asyncio
    async def test_save_all_lector_approved_files(
            self,
            session: AsyncSession,
            lector_fixture: Lector,
            lector_approved_file_fixture: LectorApprovedFile
    ):
        # when
        lector_approved_files = await lector_approved_file_repository.save_all(session, [lector_approved_file_fixture])

        # then
        assert lector_approved_files == [lector_approved_file_fixture]

    @pytest.mark.asyncio
    async def test_find_all_lector_approved_files_by_lector_id(
            self,
            session: AsyncSession,
            lector_fixture: Lector,
            lector_approved_file_fixture: LectorApprovedFile
    ):
        # when
        lector_approved_files = await lector_approved_file_repository.find_all_by_lector_id(session, lector_fixture.id)

        # then
        assert lector_approved_files == [lector_approved_file_fixture]

    @pytest.mark.asyncio
    async def test_delete_all_lector_approved_files_by_lector_id(
            self,
            session: AsyncSession,
            lector_fixture: Lector
    ):
        # when
        await lector_approved_file_repository.delete_all_by_lector_id(session, lector_fixture.id)

        # then
        assert await lector_approved_file_repository.find_all_by_lector_id(session, lector_fixture.id) == []
