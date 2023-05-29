import pytest

from claon_admin.service.user import UserService


@pytest.mark.describe("Test case for check nickname duplication")
class TestCheckNicknameDuplication(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case: not duplicated nickname")
    async def test_exist_by_not_existing_nickname(
            self,
            mock_repo: dict,
            user_service: UserService
    ):
        # given
        mock_repo["user"].exist_by_nickname.side_effect = [False]

        # when
        result = await user_service.check_nickname_duplication(None, "not_existing_nickname")

        # then
        assert result.is_duplicated is False

    @pytest.mark.asyncio
    @pytest.mark.it("Success case: duplicated nickname")
    async def test_exist_by_existing_nickname(
            self,
            mock_repo: dict,
            user_service: UserService
    ):
        # given
        mock_repo["user"].exist_by_nickname.side_effect = [True]

        # when
        result = await user_service.check_nickname_duplication(None, "existing_nickname")

        # then
        assert result.is_duplicated is True
