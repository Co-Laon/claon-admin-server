from unittest.mock import patch, AsyncMock

import pytest
from fastapi import UploadFile

from claon_admin.common.enum import CenterUploadPurpose
from claon_admin.common.error.exception import BadRequestException, ErrorCode
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for upload file")
class TestUploadFile(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case: upload image")
    @patch("claon_admin.service.center.upload_file")
    async def test_upload_file_with_purpose(
            self,
            mock_upload_file,
            center_service: CenterService
    ):
        # given
        upload_file = AsyncMock(spec=UploadFile)
        upload_file.filename = "test.png"
        mock_upload_file.return_value = "https://test_upload_center/center/image/uuid.png"
        purpose = CenterUploadPurpose.IMAGE

        # when
        result = await center_service.upload_file(purpose, upload_file)

        # then
        assert result.file_url.split('.')[-1] == "png"
        assert result.file_url.split('/')[-2] == "image"
        assert result.file_url.split('/')[-3] == "center"

    @pytest.mark.asyncio
    @pytest.mark.it("Success case: upload proof")
    @patch("claon_admin.service.center.upload_file")
    async def test_upload_file_with_purpose_proof(
            self,
            mock_upload_file,
            center_service: CenterService
    ):
        # given
        upload_file = AsyncMock(spec=UploadFile)
        upload_file.filename = "test.pdf"
        mock_upload_file.return_value = "https://test_upload_center_proof/center/proof/uuid.pdf"
        purpose = CenterUploadPurpose.PROOF

        # when
        result = await center_service.upload_file(purpose, upload_file)

        # then
        assert result.file_url.split('.')[-1] == "pdf"
        assert result.file_url.split('/')[-2] == "proof"
        assert result.file_url.split('/')[-3] == "center"

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: invalid file format")
    async def test_upload_file_with_invalid_format(self, center_service: CenterService):
        # given
        upload_file = AsyncMock(spec=UploadFile)
        upload_file.filename = "test.gif"
        purpose = CenterUploadPurpose.PROOF

        with pytest.raises(BadRequestException) as exception:
            # when
            await center_service.upload_file(purpose, upload_file)

        # then
        assert exception.value.code == ErrorCode.INVALID_FORMAT

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: invalid file format when upload image")
    async def test_upload_file_with_second_invalid_format(self, center_service: CenterService):
        # given
        upload_file = AsyncMock(spec=UploadFile)
        upload_file.filename = "test.pdf"
        purpose = CenterUploadPurpose.IMAGE

        with pytest.raises(BadRequestException) as exception:
            # when
            await center_service.upload_file(purpose, upload_file)

        # then
        assert exception.value.code == ErrorCode.INVALID_FORMAT
