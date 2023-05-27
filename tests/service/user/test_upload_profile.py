from unittest.mock import patch, AsyncMock

import pytest
from fastapi import UploadFile

from claon_admin.common.error.exception import BadRequestException, ErrorCode
from claon_admin.service.user import UserService


@pytest.mark.describe("Test case for upload profile")
class TestUploadProfile(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    @patch("claon_admin.service.user.upload_file")
    async def test_upload_profile(
            self,
            mock_upload_file,
            user_service: UserService
    ):
        # given
        upload_file = AsyncMock(spec=UploadFile)
        upload_file.filename = "test.png"
        mock_upload_file.return_value = "https://test_upload_profile/user/profile/uuid.png"

        # when
        result = await user_service.upload_profile(upload_file)

        # then
        assert result.file_url.split('.')[-1] == "png"
        assert result.file_url.split('/')[-2] == "profile"
        assert result.file_url.split('/')[-3] == "user"

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: invalid file format")
    async def test_upload_profile_with_invalid_format(self, user_service: UserService):
        # given
        upload_file = AsyncMock(spec=UploadFile)
        upload_file.filename = "test.gif"

        with pytest.raises(BadRequestException) as exception:
            # when
            await user_service.upload_profile(upload_file)

        # then
        assert exception.value.code == ErrorCode.INVALID_FORMAT
