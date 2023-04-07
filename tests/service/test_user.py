from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.user import User, UserRepository
from claon_admin.service.user import UserService


@pytest.fixture(scope="session")
async def user_fixture(session: AsyncSession, user_fixture: User):
    yield user_fixture


@pytest.mark.asyncio
async def test_exist_by_not_existing_nickname(session: AsyncSession, user_fixture: User):
    # given
    mock_user_repository = AsyncMock(spec=UserRepository)
    mock_user_repository.exist_by_nickname.side_effect = [False]

    # when
    user_service = UserService(mock_user_repository)
    result = await user_service.check_nickname_duplication(session, "not_existing_nickname")

    # then
    assert result.is_duplicated is False


async def test_exist_by_existing_nickname(session: AsyncSession, user_fixture: User):
    # given
    mock_user_repository = AsyncMock(spec=UserRepository)
    mock_user_repository.exist_by_nickname.side_effect = [True]

    # when
    user_service = UserService(mock_user_repository)
    result = await user_service.check_nickname_duplication(session, "existing_nickname")

    # then
    assert result.is_duplicated is True
