from unittest.mock import AsyncMock, patch

import pytest
from fastapi import UploadFile

from claon_admin.common.error.exception import BadRequestException, ErrorCode
from claon_admin.common.enum import LectorUploadPurpose
from claon_admin.model.file import UploadFileResponseDto
from claon_admin.service.user import UserService


@pytest.mark.describe("Test case for upload file")
class TestUploadFile(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    @patch("claon_admin.service.user.upload_file")
    async def test_upload_file_with_purpose(
            self,
            mock_upload_file,
            user_service: UserService
    ):
        # given
        upload_file = AsyncMock(spec=UploadFile)
        upload_file.filename = "test.pdf"
        mock_upload_file.return_value = "https://test_upload_lector_proof/lector/proof/uuid.pdf"
        purpose = LectorUploadPurpose.PROOF

        # when
        result: UploadFileResponseDto = await user_service.upload_file(purpose, upload_file)

        # then
        assert result.file_url.split('.')[-1] == "pdf"
        assert result.file_url.split('/')[-2] == "proof"
        assert result.file_url.split('/')[-3] == "lector"

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: invalid file format")
    async def test_upload_file_with_invalid_format(self, user_service: UserService):
        # given
        upload_file = AsyncMock(spec=UploadFile)
        upload_file.filename = "test.gif"
        purpose = LectorUploadPurpose.PROOF

        with pytest.raises(BadRequestException) as exception:
            # when
            await user_service.upload_file(purpose, upload_file)

        # then
        assert exception.value.code == ErrorCode.INVALID_FORMAT
