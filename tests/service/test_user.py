import uuid
from datetime import date
from typing import List
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import BadRequestException, ErrorCode
from claon_admin.common.util.pagination import PaginationFactory
from claon_admin.common.util.oauth import GoogleUserInfoProvider, OAuthUserInfoProviderSupplier, KakaoUserInfoProvider
from claon_admin.model.auth import OAuthUserInfoDto
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterAuthRequestDto, CenterFeeDto, CenterHoldDto, CenterWallDto, \
    CenterOperatingTimeDto, UploadFileResponseDto
from claon_admin.common.enum import OAuthProvider, LectorUploadPurpose
from claon_admin.common.enum import WallType, Role
from claon_admin.model.user import LectorRequestDto, LectorContestDto, LectorCertificateDto, \
    LectorCareerDto, UserProfileDto
from claon_admin.model.user import SignInRequestDto, JwtResponseDto
from claon_admin.schema.center import CenterRepository, Center, CenterHoldRepository, CenterWallRepository, \
    CenterApprovedFileRepository, CenterHold, CenterWall, CenterApprovedFile, CenterImage, OperatingTime, Utility, \
    CenterFee, CenterFeeImage, CenterFeeRepository
from claon_admin.schema.user import User, UserRepository, LectorRepository, Lector, LectorApprovedFileRepository, \
    LectorApprovedFile, Contest, Certificate, Career
from claon_admin.service.user import UserService


@pytest.fixture
def mock_repo():
    user_repository = AsyncMock(spec=UserRepository)
    lector_repository = AsyncMock(spec=LectorRepository)
    lector_approved_file_repository = AsyncMock(spec=LectorApprovedFileRepository)
    center_repository = AsyncMock(spec=CenterRepository)
    center_approved_file_repository = AsyncMock(spec=CenterApprovedFileRepository)
    center_fee_repository = AsyncMock(spec=CenterFeeRepository)
    center_hold_repository = AsyncMock(spec=CenterHoldRepository)
    center_wall_repository = AsyncMock(spec=CenterWallRepository)
    pagination_factory = AsyncMock(spec=PaginationFactory)

    return {
        "user": user_repository,
        "lector": lector_repository,
        "lector_approved_file": lector_approved_file_repository,
        "center": center_repository,
        "center_approved_file": center_approved_file_repository,
        "center_fee": center_fee_repository,
        "center_hold": center_hold_repository,
        "center_wall": center_wall_repository,
        "pagination_factory" : pagination_factory
    }


@pytest.fixture
def mock_supplier():
    return AsyncMock(OAuthUserInfoProviderSupplier)


@pytest.fixture
def user_service(mock_repo: dict, mock_supplier: OAuthUserInfoProviderSupplier):
    return UserService(
        mock_repo["user"],
        mock_repo["lector"],
        mock_repo["lector_approved_file"],
        mock_repo["center"],
        mock_repo["center_approved_file"],
        mock_repo["center_fee"],
        mock_repo["center_hold"],
        mock_repo["center_wall"],
        mock_supplier,
        mock_repo["pagination_factory"]
    )


@pytest.fixture
def mock_user():
    yield User(
        id=str(uuid.uuid4()),
        oauth_id="oauth_id",
        nickname="nickname",
        profile_img="profile_img",
        sns="sns",
        email="test@test.com",
        instagram_name="instagram_name",
        role=Role.PENDING
    )


@pytest.fixture
def lector_request_dto(session: AsyncSession, mock_user: User):
    yield LectorRequestDto(
        profile=UserProfileDto(
            profile_image=mock_user.profile_img,
            nickname=mock_user.nickname,
            email=mock_user.email,
            instagram_nickname=mock_user.instagram_name,
            role=mock_user.role
        ),
        is_setter=True,
        contest_list=[
            LectorContestDto(
                year=2021,
                title='testtitle',
                name='testname'
            )
        ],
        certificate_list=[
            LectorCertificateDto(
                acquisition_date=date.fromisoformat('2012-10-15'),
                rate=4,
                name='testcertificate'
            )
        ],
        career_list=[
            LectorCareerDto(
                start_date=date.fromisoformat('2016-01-01'),
                end_date=date.fromisoformat('2020-01-01'),
                name='testcareer'
            )
        ],
        proof_list=['https://test.com/test.pdf']
    )


@pytest.fixture
async def center_request_dto(session: AsyncSession, mock_user: User):
    yield CenterAuthRequestDto(
        profile=UserProfileDto(
            profile_image=mock_user.profile_img,
            nickname=mock_user.nickname,
            email=mock_user.email,
            instagram_nickname=mock_user.instagram_name,
            role=mock_user.role
        ),
        profile_image="https://test.profile.png",
        name="test center",
        address="test_address",
        detail_address="test_detail_address",
        tel="010-1234-5678",
        web_url="http://test.com",
        instagram_name="test_instagram",
        youtube_code="@test",
        image_list=["https://test.image.png"],
        utility_list=["test_utility"],
        fee_image_list=["https://test.fee.png"],
        operating_time_list=[CenterOperatingTimeDto(day_of_week="월", start_time="09:00", end_time="18:00")],
        fee_list=[CenterFeeDto(name="fee", price=1000, count=10)],
        hold_list=[CenterHoldDto(name="hold", difficulty="hard", is_color=False)],
        wall_list=[CenterWallDto(name="wall", wall_type=WallType.ENDURANCE)],
        proof_list=["https://example.com/approved.jpg"]
    )


@pytest.fixture
def mock_lector(mock_user: User):
    yield Lector(
        id=str(uuid.uuid4()),
        user=mock_user,
        is_setter=True,
        contest=[Contest(year=2021, title="title", name="name")],
        certificate=[
            Certificate(
                acquisition_date=date.fromisoformat("2012-10-15"),
                rate=4,
                name="certificate"
            )
        ],
        career=[
            Career(
                start_date=date.fromisoformat("2016-01-01"),
                end_date=date.fromisoformat("2020-01-01"),
                name="career"
            )
        ],
        approved=False
    )


@pytest.fixture
def mock_lector_approved_files(mock_lector: Lector):
    yield LectorApprovedFile(
        id=str(uuid.uuid4()),
        lector=mock_lector,
        url="https://test.com/test.pdf"
    )


@pytest.fixture
def mock_center(mock_user: User):
    yield Center(
        id=str(uuid.uuid4()),
        user=mock_user,
        name="test center",
        profile_img="https://test.profile.png",
        address="test_address",
        detail_address="test_detail_address",
        tel="010-1234-5678",
        web_url="http://test.com",
        instagram_name="test_instagram",
        youtube_url="https://www.youtube.com/@test",
        center_img=[CenterImage(url="https://test.image.png")],
        operating_time=[OperatingTime(day_of_week="월", start_time="09:00", end_time="18:00")],
        utility=[Utility(name="test_utility")],
        fee_img=[CenterFeeImage(url="https://test.fee.png")],
        approved=False
    )


@pytest.fixture
def mock_center_approved_files(mock_user: User, mock_center: Center):
    yield [
        CenterApprovedFile(
            id=str(uuid.uuid4()),
            user=mock_user,
            center=mock_center,
            url="https://example.com/approved.jpg"
        )
    ]


@pytest.fixture
def mock_center_fees(mock_center: Center):
    yield [
        CenterFee(
            id=str(uuid.uuid4()),
            center=mock_center,
            name="fee",
            price=1000,
            count=10
        )
    ]


@pytest.fixture
def mock_center_holds(mock_center: Center):
    yield [
        CenterHold(
            id=str(uuid.uuid4()),
            center=mock_center,
            name="hold",
            difficulty="hard",
            is_color=False
        )
    ]


@pytest.fixture
def mock_center_walls(mock_center: Center):
    yield [
        CenterWall(
            id=str(uuid.uuid4()),
            center=mock_center,
            name="wall",
            type=WallType.ENDURANCE.value
        )
    ]


@pytest.mark.asyncio
async def test_sign_up_center(
        session: AsyncSession,
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
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.PENDING)
    mock_repo["user"].exist_by_nickname.side_effect = [False]
    mock_repo["center"].save.side_effect = [mock_center]
    mock_repo["center_fee"].save_all.side_effect = [mock_center_fees]
    mock_repo["center_hold"].save_all.side_effect = [mock_center_holds]
    mock_repo["center_wall"].save_all.side_effect = [mock_center_walls]
    mock_repo["center_approved_file"].save_all.side_effect = [mock_center_approved_files]

    # when
    result = await user_service.sign_up_center(session, request_user, center_request_dto)

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
    assert result.fee_image_list == center_request_dto.fee_image_list
    assert result.operating_time_list == center_request_dto.operating_time_list
    assert result.fee_list == center_request_dto.fee_list
    assert result.hold_list == center_request_dto.hold_list
    assert result.wall_list == center_request_dto.wall_list


@pytest.mark.asyncio
async def test_sign_up_center_existing_nickname(
        session: AsyncSession,
        mock_repo: dict,
        user_service: UserService,
        center_request_dto: CenterAuthRequestDto
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.PENDING)
    mock_repo["user"].exist_by_nickname.side_effect = [True]

    with pytest.raises(BadRequestException) as exception:
        # when
        await user_service.sign_up_center(session, request_user, center_request_dto)

    # then
    assert exception.value.code == ErrorCode.DUPLICATED_NICKNAME


@pytest.mark.asyncio
async def test_sign_up_center_already_sign_up(
        session: AsyncSession,
        mock_repo: dict,
        user_service: UserService,
        center_request_dto: CenterAuthRequestDto
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.CENTER_ADMIN)

    with pytest.raises(BadRequestException) as exception:
        # when
        await user_service.sign_up_center(session, request_user, center_request_dto)

    # then
    assert exception.value.code == ErrorCode.USER_ALREADY_SIGNED_UP


@pytest.mark.asyncio
async def test_sign_up_lector(
        session: AsyncSession,
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

    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.PENDING)

    # when
    result = await user_service.sign_up_lector(session, request_user, lector_request_dto)

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
        session: AsyncSession,
        mock_repo: dict,
        user_service: UserService,
        lector_request_dto: LectorRequestDto
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.PENDING)
    mock_repo["user"].exist_by_nickname.side_effect = [True]

    with pytest.raises(BadRequestException) as exception:
        # when
        await user_service.sign_up_lector(session, request_user, lector_request_dto)

    # then
    assert exception.value.code == ErrorCode.DUPLICATED_NICKNAME


@pytest.mark.asyncio
async def test_sign_up_lector_already_sign_up(
        session: AsyncSession,
        mock_repo: dict,
        user_service: UserService,
        lector_request_dto: LectorRequestDto
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.LECTOR)

    with pytest.raises(BadRequestException) as exception:
        # when
        await user_service.sign_up_lector(session, request_user, lector_request_dto)

    # then
    assert exception.value.code == ErrorCode.USER_ALREADY_SIGNED_UP


@pytest.mark.asyncio
async def test_exist_by_not_existing_nickname(
        session: AsyncSession,
        mock_repo: dict,
        user_service: UserService
):
    # given
    mock_repo["user"].exist_by_nickname.side_effect = [False]

    # when
    result = await user_service.check_nickname_duplication(session, "not_existing_nickname")

    # then
    assert result.is_duplicated is False


@pytest.mark.asyncio
async def test_exist_by_existing_nickname(
        session: AsyncSession,
        mock_repo: dict,
        user_service: UserService
):
    # given
    mock_repo["user"].exist_by_nickname.side_effect = [True]

    # when
    result = await user_service.check_nickname_duplication(session, "existing_nickname")

    # then
    assert result.is_duplicated is True


@pytest.mark.asyncio
@patch("claon_admin.service.user.create_access_token")
@patch("claon_admin.service.user.create_refresh_token")
async def test_sign_in_with_google(
        mock_create_access_token,
        mock_create_refresh_token,
        session: AsyncSession,
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
    result: JwtResponseDto = await user_service.sign_in(session, provider_name, sign_in_request_dto)

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
        session: AsyncSession,
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
    result: JwtResponseDto = await user_service.sign_in(session, provider_name, sign_in_request_dto)

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
        session: AsyncSession,
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
    result: JwtResponseDto = await user_service.sign_in(session, provider_name, sign_in_request_dto)

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
        session: AsyncSession,
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
    result: JwtResponseDto = await user_service.sign_in(session, provider_name, sign_in_request_dto)

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
