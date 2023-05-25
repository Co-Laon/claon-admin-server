import uuid
from datetime import date
from unittest.mock import AsyncMock

import pytest

from claon_admin.schema.center import CenterRepository, CenterApprovedFileRepository
from claon_admin.schema.user import UserRepository, LectorRepository, LectorApprovedFileRepository
from claon_admin.service.admin import AdminService
from claon_admin.common.enum import Role, WallType
from claon_admin.schema.center import Center, CenterApprovedFile, CenterImage, OperatingTime, Utility, CenterFeeImage
from claon_admin.schema.user import Lector, LectorApprovedFile, User, Contest, Certificate, Career
from claon_admin.model.admin import CenterResponseDto, LectorResponseDto
from claon_admin.model.user import LectorCareerDto, LectorCertificateDto, LectorContestDto, UserProfileResponseDto
from claon_admin.model.center import CenterFeeDto, CenterHoldDto, CenterOperatingTimeDto, CenterWallDto


@pytest.fixture
def mock_repo():
    user_repository = AsyncMock(spec=UserRepository)
    lector_repository = AsyncMock(spec=LectorRepository)
    lector_approved_file_repository = AsyncMock(spec=LectorApprovedFileRepository)
    center_repository = AsyncMock(spec=CenterRepository)
    center_approved_file_repository = AsyncMock(spec=CenterApprovedFileRepository)

    return {
        "user": user_repository,
        "lector": lector_repository,
        "lector_approved_file": lector_approved_file_repository,
        "center": center_repository,
        "center_approved_file": center_approved_file_repository
    }


@pytest.fixture
def admin_service(mock_repo: dict):
    return AdminService(
        mock_repo["user"],
        mock_repo["lector"],
        mock_repo["lector_approved_file"],
        mock_repo["center"],
        mock_repo["center_approved_file"]
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
def lector_response_dto(mock_user: User):
    yield LectorResponseDto(
        user_profile=UserProfileResponseDto.from_entity(mock_user),
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
async def center_response_dto(mock_user: User):
    yield CenterResponseDto(
        user_profile=UserProfileResponseDto.from_entity(mock_user),
        cetner_id=str(uuid.uuid4()),
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
        fee_list=[CenterFeeDto(name="test_fee_name", price=1000, count=10)],
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
    yield [
        LectorApprovedFile(
            id=str(uuid.uuid4()),
            lector=mock_lector,
            url="https://test.com/test.pdf"
        )
    ]


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
