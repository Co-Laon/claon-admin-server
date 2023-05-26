from typing import List
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import UploadFile

from claon_admin.common.error.exception import BadRequestException, ErrorCode
from claon_admin.common.util.oauth import GoogleUserInfoProvider, OAuthUserInfoProviderSupplier, KakaoUserInfoProvider
from claon_admin.model.auth import OAuthUserInfoDto
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterAuthRequestDto
from claon_admin.common.enum import OAuthProvider, LectorUploadPurpose
from claon_admin.common.enum import Role
from claon_admin.model.file import UploadFileResponseDto
from claon_admin.model.user import LectorRequestDto, LectorContestDto, LectorCertificateDto, LectorCareerDto
from claon_admin.model.user import SignInRequestDto, JwtResponseDto
from claon_admin.schema.center import Center,CenterHold, CenterWall, CenterApprovedFile, CenterFee
from claon_admin.schema.user import User, Lector, LectorApprovedFile
from claon_admin.service.user import UserService


@pytest.mark.asyncio
async def test_sign_up_center(
        mock_repo: dict,
        user_service: UserService,
        mock_user: User,
        mock_center: Center,
        mock_center_fees: List[CenterFee],
        mock_center_holds: List[CenterHold],
        mock_center_walls: List[CenterWall],
        mock_center_approved_files: List[CenterApprovedFile],
        center_request_dto: CenterAuthRequestDto
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
    mock_repo["user"].exist_by_nickname.side_effect = [False]
    mock_repo["center"].save.side_effect = [mock_center]
    mock_repo["center_fee"].save_all.side_effect = [mock_center_fees]
    mock_repo["center_hold"].save_all.side_effect = [mock_center_holds]
    mock_repo["center_wall"].save_all.side_effect = [mock_center_walls]
    mock_repo["center_approved_file"].save_all.side_effect = [mock_center_approved_files]

    # when
    result = await user_service.sign_up_center(None, request_user, center_request_dto)

    # then
    assert result.profile_image == center_request_dto.profile_image
    assert result.name == center_request_dto.name
    assert result.address == center_request_dto.address
    assert result.detail_address == center_request_dto.detail_address
    assert result.tel == center_request_dto.tel
    assert result.web_url == center_request_dto.web_url
    assert result.instagram_name == center_request_dto.instagram_name
    assert result.youtube_code == center_request_dto.youtube_code
    assert result.image_list == center_request_dto.image_list
    assert result.utility_list == center_request_dto.utility_list
    assert result.operating_time_list == center_request_dto.operating_time_list
    assert result.hold_list == center_request_dto.hold_list
    assert result.wall_list == center_request_dto.wall_list


@pytest.mark.asyncio
async def test_sign_up_center_existing_nickname(
        mock_repo: dict,
        user_service: UserService,
        center_request_dto: CenterAuthRequestDto
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
    mock_repo["user"].exist_by_nickname.side_effect = [True]

    with pytest.raises(BadRequestException) as exception:
        # when
        await user_service.sign_up_center(None, request_user, center_request_dto)

    # then
    assert exception.value.code == ErrorCode.DUPLICATED_NICKNAME


@pytest.mark.asyncio
async def test_sign_up_center_already_sign_up(
        mock_repo: dict,
        user_service: UserService,
        center_request_dto: CenterAuthRequestDto
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)

    with pytest.raises(BadRequestException) as exception:
        # when
        await user_service.sign_up_center(None, request_user, center_request_dto)

    # then
    assert exception.value.code == ErrorCode.USER_ALREADY_SIGNED_UP


@pytest.mark.asyncio
async def test_sign_up_lector(
        mock_repo: dict,
        user_service: UserService,
        mock_user: User,
        mock_lector: Lector,
        mock_lector_approved_files: List[LectorApprovedFile],
        lector_request_dto: LectorRequestDto
):
    # given
    mock_repo["user"].exist_by_nickname.side_effect = [False]
    mock_repo["lector"].save.side_effect = [mock_lector]
    mock_repo["lector_approved_file"].save_all.side_effect = [mock_lector_approved_files]

    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)

    # when
    result = await user_service.sign_up_lector(None, request_user, lector_request_dto)

    # then
    assert result.is_setter == lector_request_dto.is_setter
    assert result.total_experience == 4
    assert result.contest_list == [
        LectorContestDto(
            year=e.year,
            title=e.title,
            name=e.name
        ) for e in mock_lector.contest
    ]
    assert result.certificate_list == [
        LectorCertificateDto(
            acquisition_date=e.acquisition_date,
            rate=e.rate,
            name=e.name
        ) for e in mock_lector.certificate
    ]
    assert result.career_list == [
        LectorCareerDto(
            start_date=e.start_date,
            end_date=e.end_date,
            name=e.name
        ) for e in mock_lector.career
    ]
    assert result.approved is False


@pytest.mark.asyncio
async def test_sign_up_lector_existing_nickname(
        mock_repo: dict,
        user_service: UserService,
        lector_request_dto: LectorRequestDto
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
    mock_repo["user"].exist_by_nickname.side_effect = [True]

    with pytest.raises(BadRequestException) as exception:
        # when
        await user_service.sign_up_lector(None, request_user, lector_request_dto)

    # then
    assert exception.value.code == ErrorCode.DUPLICATED_NICKNAME


@pytest.mark.asyncio
async def test_sign_up_lector_already_sign_up(
        mock_repo: dict,
        user_service: UserService,
        lector_request_dto: LectorRequestDto
):
    # given
    request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.LECTOR)

    with pytest.raises(BadRequestException) as exception:
        # when
        await user_service.sign_up_lector(None, request_user, lector_request_dto)

    # then
    assert exception.value.code == ErrorCode.USER_ALREADY_SIGNED_UP


@pytest.mark.asyncio
async def test_exist_by_not_existing_nickname(
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
async def test_exist_by_existing_nickname(
        mock_repo: dict,
        user_service: UserService
):
    # given
    mock_repo["user"].exist_by_nickname.side_effect = [True]

    # when
    result = await user_service.check_nickname_duplication(None, "existing_nickname")

    # then
    assert result.is_duplicated is True


@pytest.mark.asyncio
@patch("claon_admin.service.user.create_access_token")
@patch("claon_admin.service.user.create_refresh_token")
async def test_sign_in_with_google(
        mock_create_access_token,
        mock_create_refresh_token,
        mock_repo: dict,
        mock_user: User,
        mock_supplier: OAuthUserInfoProviderSupplier,
        user_service: UserService
):
    # given
    mock_user.role = Role.USER
    mock_repo["user"].find_by_oauth_id_and_sns.side_effect = [mock_user]

    sign_in_request_dto = SignInRequestDto(id_token="test_id_token")
    provider_name = OAuthProvider.GOOGLE

    oauth_user_info_dto = OAuthUserInfoDto(oauth_id="oauth_id", sns_email="test_sns")
    mock_provider = AsyncMock(spec=GoogleUserInfoProvider)
    mock_provider.get_user_info.return_value = oauth_user_info_dto

    mock_supplier.get_provider.return_value = mock_provider

    mock_create_access_token.return_value = "test_access_token"
    mock_create_refresh_token.return_value = "test_refresh_token"

    # when
    result: JwtResponseDto = await user_service.sign_in(None, provider_name, sign_in_request_dto)

    # then
    assert result.access_token is not None
    assert result.refresh_token is not None
    assert result.is_signed_up is True


@pytest.mark.asyncio
@patch("claon_admin.service.user.create_access_token")
@patch("claon_admin.service.user.create_refresh_token")
async def test_sign_in_with_google_new_user(
        mock_create_access_token,
        mock_create_refresh_token,
        mock_repo: dict,
        mock_user: User,
        mock_supplier: OAuthUserInfoProviderSupplier,
        user_service: UserService
):
    # given
    mock_repo["user"].find_by_oauth_id_and_sns.side_effect = [None]
    mock_repo["user"].save.side_effect = [mock_user]

    sign_in_request_dto = SignInRequestDto(id_token="test_id_token")
    provider_name = OAuthProvider.GOOGLE

    oauth_user_info_dto = OAuthUserInfoDto(oauth_id="oauth_id", sns_email="test_sns")
    mock_provider = AsyncMock(spec=GoogleUserInfoProvider)
    mock_provider.get_user_info.return_value = oauth_user_info_dto

    mock_supplier.get_provider.return_value = mock_provider

    mock_create_access_token.return_value = "test_access_token"
    mock_create_refresh_token.return_value = "test_refresh_token"

    # when
    result: JwtResponseDto = await user_service.sign_in(None, provider_name, sign_in_request_dto)

    # then
    assert result.access_token is not None
    assert result.refresh_token is not None
    assert result.is_signed_up is False


@pytest.mark.asyncio
@patch("claon_admin.service.user.create_access_token")
@patch("claon_admin.service.user.create_refresh_token")
async def test_sign_in_with_kakao(
        mock_create_access_token,
        mock_create_refresh_token,
        mock_repo: dict,
        mock_user: User,
        mock_supplier: OAuthUserInfoProviderSupplier,
        user_service: UserService
):
    # given
    mock_user.role = Role.USER
    mock_repo["user"].find_by_oauth_id_and_sns.side_effect = [mock_user]

    sign_in_request_dto = SignInRequestDto(id_token="test_id_token")
    provider_name = OAuthProvider.KAKAO

    oauth_user_info_dto = OAuthUserInfoDto(oauth_id="oauth_id", sns_email="test_sns")
    mock_provider = AsyncMock(spec=KakaoUserInfoProvider)
    mock_provider.get_user_info.return_value = oauth_user_info_dto

    mock_supplier.get_provider.return_value = mock_provider

    mock_create_access_token.return_value = "test_access_token"
    mock_create_refresh_token.return_value = "test_refresh_token"

    # when
    result: JwtResponseDto = await user_service.sign_in(None, provider_name, sign_in_request_dto)

    # then
    assert result.access_token is not None
    assert result.refresh_token is not None
    assert result.is_signed_up is True


@pytest.mark.asyncio
@patch("claon_admin.service.user.create_access_token")
@patch("claon_admin.service.user.create_refresh_token")
async def test_sign_in_with_kakao_new_user(
        mock_create_access_token,
        mock_create_refresh_token,
        mock_repo: dict,
        mock_user: User,
        mock_supplier: OAuthUserInfoProviderSupplier,
        user_service: UserService
):
    # given
    mock_repo["user"].find_by_oauth_id_and_sns.side_effect = [None]
    mock_repo["user"].save.side_effect = [mock_user]

    sign_in_request_dto = SignInRequestDto(id_token="test_id_token")
    provider_name = OAuthProvider.KAKAO

    oauth_user_info_dto = OAuthUserInfoDto(oauth_id="oauth_id", sns_email="test_sns")
    mock_provider = AsyncMock(spec=KakaoUserInfoProvider)
    mock_provider.get_user_info.return_value = oauth_user_info_dto

    mock_supplier.get_provider.return_value = mock_provider

    mock_create_access_token.return_value = "test_access_token"
    mock_create_refresh_token.return_value = "test_refresh_token"

    # when
    result: JwtResponseDto = await user_service.sign_in(None, provider_name, sign_in_request_dto)

    # then
    assert result.access_token is not None
    assert result.refresh_token is not None
    assert result.is_signed_up is False


@pytest.mark.asyncio
@patch("claon_admin.service.user.upload_file")
async def test_upload_profile(mock_upload_file,
                              user_service: UserService):
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
async def test_upload_profile_with_invalid_format(user_service: UserService):
    # given
    upload_file = AsyncMock(spec=UploadFile)
    upload_file.filename = "test.gif"

    with pytest.raises(BadRequestException) as exception:
        # when
        await user_service.upload_profile(upload_file)

    # then
    assert exception.value.code == ErrorCode.INVALID_FORMAT


@pytest.mark.asyncio
@patch("claon_admin.service.user.upload_file")
async def test_upload_file_with_purpose(mock_upload_file,
                                        user_service: UserService):
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
async def test_upload_file_with_invalid_format(user_service: UserService):
    # given
    upload_file = AsyncMock(spec=UploadFile)
    upload_file.filename = "test.gif"
    purpose = LectorUploadPurpose.PROOF

    with pytest.raises(BadRequestException) as exception:
        # when
        await user_service.upload_file(purpose, upload_file)

    # then
    assert exception.value.code == ErrorCode.INVALID_FORMAT
