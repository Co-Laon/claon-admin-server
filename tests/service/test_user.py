from datetime import date
from typing import List
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import BadRequestException
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterRequestDto, CenterFeeDto, CenterHoldDto, CenterWallDto, \
    CenterOperatingTimeDto
from claon_admin.model.enum import WallType, Role
from claon_admin.model.user import LectorRequestDto, UserProfileDto, LectorContestDto, LectorCertificateDto, \
    LectorCareerDto
from claon_admin.schema.center import CenterRepository, Center, CenterHoldRepository, CenterWallRepository, \
    CenterApprovedFileRepository, CenterHold, CenterWall, CenterApprovedFile, CenterImage, OperatingTime, Utility, \
    CenterFee, CenterFeeImage
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
    center_hold_repository = AsyncMock(spec=CenterHoldRepository)
    center_wall_repository = AsyncMock(spec=CenterWallRepository)

    return {
        "user": user_repository,
        "lector": lector_repository,
        "lector_approved_file": lector_approved_file_repository,
        "center": center_repository,
        "center_approved_file": center_approved_file_repository,
        "center_hold": center_hold_repository,
        "center_wall": center_wall_repository
    }


@pytest.fixture
def user_service(mock_repo: dict):
    return UserService(
        mock_repo["user"],
        mock_repo["lector"],
        mock_repo["lector_approved_file"],
        mock_repo["center"],
        mock_repo["center_approved_file"],
        mock_repo["center_hold"],
        mock_repo["center_wall"]
    )


@pytest.fixture
def lector_request_dto(session: AsyncSession, mock_user):
    yield LectorRequestDto(
        profile=UserProfileDto.from_entity(mock_user),
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
async def center_request_dto(session: AsyncSession, mock_user):
    yield CenterRequestDto(
        profile=UserProfileDto.from_entity(mock_user),
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
def mock_user():
    yield User(
        nickname="nickname",
        profile_img="profile_img",
        sns="sns",
        email="test@test.com",
        instagram_name="instagram_name",
        role=Role.PENDING
    )


@pytest.fixture
def mock_lector(mock_user: User):
    yield Lector(
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
def mock_lector_approved_files():
    yield LectorApprovedFile(
        lector=mock_lector,
        url="https://test.com/test.pdf"
    )


@pytest.fixture
def mock_center(mock_user: User):
    yield Center(
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
        fee=[CenterFee(name="test_fee_name", price=1000, count=10)],
        fee_img=[CenterFeeImage(url="https://test.fee.png")],
        approved=False
    )


@pytest.fixture
def mock_center_approved_files(mock_user: User, mock_center: Center):
    yield [
        CenterApprovedFile(
            user=mock_user,
            center=mock_center,
            url="https://example.com/approved.jpg"
        )
    ]


@pytest.fixture
def mock_center_holds(mock_center: Center):
    yield [
        CenterHold(
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
        mock_center_holds: List[CenterHold],
        mock_center_walls: List[CenterWall],
        mock_center_approved_files: List[CenterApprovedFile],
        center_request_dto: CenterRequestDto
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.PENDING)
    mock_repo["user"].exist_by_nickname.side_effect = [False]
    mock_repo["center"].save.side_effect = [mock_center]
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
async def test_sign_up_existing_center(
        session: AsyncSession,
        mock_repo: dict,
        user_service: UserService,
        center_request_dto):

    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.CENTER_ADMIN)

    # then
    with pytest.raises(BadRequestException):
        # when
        await user_service.sign_up_center(session, request_user, center_request_dto)


@pytest.mark.asyncio
async def test_sign_up_lector(
        session: AsyncSession,
        mock_repo: dict,
        user_service: UserService,
        mock_user,
        mock_lector,
        mock_lector_approved_files: LectorApprovedFile,
        lector_request_dto
):
    # given
    profile = UserProfileDto.from_entity(mock_user)
    mock_repo["user"].exist_by_nickname.side_effect = [False]
    mock_repo["lector"].save.side_effect = [mock_lector]
    mock_repo["lector_approved_file"].save_all.side_effect = [mock_lector_approved_files]

    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.PENDING)

    # when
    result = await user_service.sign_up_lector(session, request_user, lector_request_dto)

    # then
    assert result.profile == profile
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
async def test_sign_up_existing_lector(
        session: AsyncSession,
        mock_repo: dict,
        user_service: UserService,
        lector_request_dto):

    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.LECTOR)

    # then
    with pytest.raises(BadRequestException):
        # when
        await user_service.sign_up_lector(session, request_user, lector_request_dto)


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
