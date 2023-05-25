import uuid
from datetime import date
from unittest.mock import AsyncMock

import pytest

from claon_admin.common.enum import Role, WallType
from claon_admin.common.util.oauth import OAuthUserInfoProviderSupplier
from claon_admin.common.util.pagination import PaginationFactory
from claon_admin.model.admin import CenterOperatingTimeDto
from claon_admin.model.center import CenterAuthRequestDto, CenterFeeDto, CenterHoldDto, CenterWallDto
from claon_admin.model.user import LectorRequestDto, UserProfileDto, LectorContestDto, LectorCertificateDto, \
    LectorCareerDto
from claon_admin.schema.center import CenterRepository, CenterApprovedFileRepository, CenterFeeRepository, \
    CenterHoldRepository, CenterWallRepository, Center, CenterImage, OperatingTime, Utility, CenterFeeImage, \
    CenterApprovedFile, CenterFee, CenterHold, CenterWall
from claon_admin.schema.user import UserRepository, LectorRepository, LectorApprovedFileRepository, User, Lector, \
    Contest, Certificate, Career, LectorApprovedFile
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
        "pagination_factory": pagination_factory
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
def lector_request_dto(mock_user: User):
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
async def center_request_dto(mock_user: User):
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