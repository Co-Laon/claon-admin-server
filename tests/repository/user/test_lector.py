import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.user import User, Lector, LectorApprovedFile
from tests.repository.user.conftest import lector_repository, lector_approved_file_repository


@pytest.mark.describe("Test case for lector repository")
class TestLectorRepository(object):
    @pytest.mark.asyncio
    async def test_save_lector(
            self,
            session: AsyncSession,
            user_fixture: User,
            lector_fixture: Lector
    ):
        # then
        assert lector_fixture.user.id == user_fixture.id
        assert lector_fixture.user == user_fixture
        assert lector_fixture.is_setter
        assert lector_fixture.contest[0].year == 2021
        assert lector_fixture.contest[0].title == 'title'
        assert lector_fixture.contest[0].name == 'name'
        assert lector_fixture.certificate[0].acquisition_date == '2012-10-15'
        assert lector_fixture.certificate[0].rate == 4
        assert lector_fixture.certificate[0].name == 'certificate'
        assert lector_fixture.career[0].start_date == '2016-01-01'
        assert lector_fixture.career[0].end_date == '2020-01-01'
        assert lector_fixture.career[0].name == 'career'
        assert lector_fixture.approved is False

    @pytest.mark.asyncio
    async def test_delete_lector(
            self,
            session: AsyncSession,
            lector_fixture: Lector,
            lector_approved_file_fixture: LectorApprovedFile
    ):
        # when
        await lector_repository.delete(session, lector_fixture)

        # then
        assert await lector_repository.find_by_id(session, lector_fixture.id) is None
        assert await lector_approved_file_repository.find_all_by_lector_id(session, lector_fixture.id) == []

    @pytest.mark.asyncio
    async def test_find_lector_by_id(
            self,
            session: AsyncSession,
            lector_fixture: Lector
    ):
        # given
        lector_id = lector_fixture.id

        # when
        result = await lector_repository.find_by_id(session, lector_id)

        # then
        assert result == lector_fixture

    @pytest.mark.asyncio
    async def test_find_lector_by_id(
            self,
            session: AsyncSession,
            lector_fixture: Lector
    ):
        # given
        lector_id = lector_fixture.id

        # when
        result = await lector_repository.find_by_id_with_user(session, lector_id)

        # then
        assert result == lector_fixture

    @pytest.mark.asyncio
    async def test_find_lector_by_invalid_id(
            self,
            session: AsyncSession
    ):
        # given
        lector_id = "non_existing_id"

        # when
        result = await lector_repository.find_by_id(session, lector_id)

        # then
        assert result is None

    @pytest.mark.asyncio
    async def test_find_all_lector_by_approved_false(
            self,
            session: AsyncSession,
            lector_fixture: Lector
    ):
        # when
        result = await lector_repository.find_all_by_approved_false(session)

        # then
        assert result == [lector_fixture]
