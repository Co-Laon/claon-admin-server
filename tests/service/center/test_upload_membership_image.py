from unittest.mock import patch, AsyncMock

import pytest
from fastapi import UploadFile

from claon_admin.common.enum import CenterFeeUploadPurpose, Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException, BadRequestException
from claon_admin.model.auth import RequestUser
from claon_admin.schema.center import Center
from claon_admin.schema.user import User
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for upload membership image file")
class TestUploadMembershipImage(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case: upload membership(center fee) image")
    @patch("claon_admin.service.center.upload_file")
    async def test_upload_membership_image_with_purpose(
            self,
            mock_upload_file,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center,
            center_service: CenterService
    ):
        # given
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        request_user = RequestUser(id=user_fixture.id, sns="test@gamil.com", role=Role.CENTER_ADMIN)
        img_file = AsyncMock(spec=UploadFile)
        img_file.filename = "membership.jpeg"
        mock_upload_file.return_value = "https://test_membership_img/fee/image/uuid.jpeg"
        purpose = CenterFeeUploadPurpose.IMAGE

        # when
        result = await center_service.upload_membership_image(
            subject=request_user,
            center_id=center_fixture.id,
            purpose=purpose,
            file=img_file
        )

        # then
        assert result.file_url.split('.')[-1] == "jpeg"
        assert result.file_url.split('/')[-2] == "image"
        assert result.file_url.split('/')[-3] == "fee"

    @pytest.mark.asyncio
    @pytest.mark.it("Failed case: upload membership image with not exist center")
    async def test_upload_membership_image_with_not_exist_center(
            self,
            mock_repo: dict,
            center_service: CenterService
    ):
        # given
        mock_repo["center"].find_by_id.side_effect = [None]
        request_user = RequestUser(id="12345600", sns="test@gamil.com", role=Role.CENTER_ADMIN)
        img_file = AsyncMock(spec=UploadFile)
        purpose = CenterFeeUploadPurpose.IMAGE

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.upload_membership_image(
                subject=request_user,
                center_id="wrong id",
                purpose=purpose,
                file=img_file
            )

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Failed case: upload membership image with not center owner")
    async def test_upload_membership_image_with_not_center_owner(
            self,
            mock_repo: dict,
            center_fixture: Center,
            center_service: CenterService
    ):
        # given
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        request_user = RequestUser(id="123456721", sns="notowner@gmail.com", role=Role.CENTER_ADMIN)
        img_file = AsyncMock(spec=UploadFile)
        purpose = CenterFeeUploadPurpose.IMAGE

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.upload_membership_image(
                subject=request_user,
                center_id=center_fixture.id,
                purpose=purpose,
                file=img_file
            )

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE

    @pytest.mark.asyncio
    @pytest.mark.it("Failed case: upload membership image with invalid foramt")
    async def test_upload_membership_image_with_invalid_format(
            self,
            mock_repo: dict,
            user_fixture: User,
            center_fixture: Center,
            center_service: CenterService

    ):
        # given
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        request_user = RequestUser(id=user_fixture.id, sns="test@gmail.com", role=Role.CENTER_ADMIN)
        img_file = AsyncMock(spec=UploadFile)
        img_file.filename = "membership.xlsx"
        purpose = CenterFeeUploadPurpose.IMAGE

        with pytest.raises(BadRequestException) as exception:
            # when
            await center_service.upload_membership_image(
                subject=request_user,
                center_id=center_fixture.id,
                purpose=purpose,
                file=img_file
            )

        # then
        assert exception.value.code == ErrorCode.INVALID_FORMAT
