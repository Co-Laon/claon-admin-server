from datetime import date
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import BadRequestException
from claon_admin.model.center import CenterRequestDto, CenterFeeDto, CenterHoldDto, CenterWallDto, \
    CenterOperatingTimeDto
from claon_admin.model.enum import WallType, Role
from claon_admin.model.user import LectorRequestDto, UserProfileDto, LectorContestDto, LectorCertificateDto, \
    LectorCareerDto
from claon_admin.schema.center import CenterRepository, Center
from claon_admin.schema.user import User, UserRepository, LectorRepository, Lector
from claon_admin.service.user import UserService


@pytest.fixture(scope="function")
def lector_request_dto_fixture(session: AsyncSession, user_fixture: User):
    lector_request_dto = LectorRequestDto(
        profile=UserProfileDto.from_entity(user_fixture),
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

    yield lector_request_dto


@pytest.fixture(scope="function")
def center_request_dto_fixture(session: AsyncSession, user_fixture: User):
    center_request_dto = CenterRequestDto(
        profile=UserProfileDto.from_entity(user_fixture),
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
        hold_list=[CenterHoldDto(name="test_hold", difficulty="#ffffff", is_color=True)],
        wall_list=[CenterWallDto(name="test_wall", wall_type=WallType.ENDURANCE)],
        proof_list=["proof.pdf"]
    )

    yield center_request_dto


@pytest.mark.asyncio
async def test_sign_up_center(
        session: AsyncSession,
        user_fixture: User,
        center_fixture: Center,
        center_request_dto_fixture: CenterRequestDto
):
    # given
    mock_user_repository = AsyncMock(spec=UserRepository)
    mock_lector_repository = AsyncMock(spec=LectorRepository)
    mock_center_repository = AsyncMock(spec=CenterRepository)

    mock_user_repository.find_by_nickname.side_effect = [user_fixture]
    mock_center_repository.save.side_effect = [center_fixture]

    # when
    user_service = UserService(mock_user_repository, mock_lector_repository, mock_center_repository)
    result = await user_service.sign_up_center(session, center_request_dto_fixture)

    # then
    assert result.profile_image == center_request_dto_fixture.profile_image
    assert result.name == center_request_dto_fixture.name
    assert result.address == center_request_dto_fixture.address
    assert result.detail_address == center_request_dto_fixture.detail_address
    assert result.tel == center_request_dto_fixture.tel
    assert result.web_url == center_request_dto_fixture.web_url
    assert result.instagram_name == center_request_dto_fixture.instagram_name
    assert result.youtube_code == center_request_dto_fixture.youtube_code
    assert result.image_list == center_request_dto_fixture.image_list
    assert result.utility_list == center_request_dto_fixture.utility_list
    assert result.fee_image_list == center_request_dto_fixture.fee_image_list
    assert result.operating_time_list == center_request_dto_fixture.operating_time_list
    assert result.fee_list == center_request_dto_fixture.fee_list
    assert result.hold_list == center_request_dto_fixture.hold_list
    assert result.wall_list == center_request_dto_fixture.wall_list


@pytest.mark.asyncio
async def test_sign_up_existing_center(
        session: AsyncSession,
        center_request_dto_fixture: CenterRequestDto):

    # given
    mock_user_repository = AsyncMock(spec=UserRepository)
    mock_lector_repository = AsyncMock(spec=LectorRepository)
    mock_center_repository = AsyncMock(spec=CenterRepository)
    center_request_dto_fixture.profile.role = Role.CENTER_ADMIN

    # when
    user_service = UserService(mock_user_repository, mock_lector_repository, mock_center_repository)

    # then
    with pytest.raises(BadRequestException):
        await user_service.sign_up_center(session, center_request_dto_fixture)


@pytest.mark.asyncio
async def test_sign_up_lector(
        session: AsyncSession,
        user_fixture: User,
        lector_fixture: Lector,
        lector_request_dto_fixture: LectorRequestDto
):
    # given
    mock_user_repository = AsyncMock(spec=UserRepository)
    mock_lector_repository = AsyncMock(spec=LectorRepository)
    mock_center_repository = AsyncMock(spec=CenterRepository)

    profile = UserProfileDto.from_entity(user_fixture)

    mock_user_repository.find_by_nickname.side_effect = [user_fixture]
    mock_lector_repository.save.side_effect = [lector_fixture]

    # when
    user_service = UserService(mock_user_repository, mock_lector_repository, mock_center_repository)
    result = await user_service.sign_up_lector(session, lector_request_dto_fixture)

    # then
    assert result.profile == profile


@pytest.mark.asyncio
async def test_sign_up_existing_lector(
        session: AsyncSession,
        lector_request_dto_fixture: LectorRequestDto):

    # given
    mock_user_repository = AsyncMock(spec=UserRepository)
    mock_lector_repository = AsyncMock(spec=LectorRepository)
    mock_center_repository = AsyncMock(spec=CenterRepository)
    lector_request_dto_fixture.profile.role = Role.LECTOR

    # when
    user_service = UserService(mock_user_repository, mock_lector_repository, mock_center_repository)

    # then
    with pytest.raises(BadRequestException):
        await user_service.sign_up_lector(session, lector_request_dto_fixture)


@pytest.mark.asyncio
async def test_exist_by_not_existing_nickname(
        session: AsyncSession
):
    # given
    mock_user_repository = AsyncMock(spec=UserRepository)
    mock_lector_repository = AsyncMock(spec=LectorRepository)
    mock_center_repository = AsyncMock(spec=CenterRepository)
    mock_user_repository.exist_by_nickname.side_effect = [False]

    # when
    user_service = UserService(mock_user_repository, mock_lector_repository, mock_center_repository)
    result = await user_service.check_nickname_duplication(session, "not_existing_nickname")

    # then
    assert result.is_duplicated is False


async def test_exist_by_existing_nickname(
        session: AsyncSession
):
    # given
    mock_user_repository = AsyncMock(spec=UserRepository)
    mock_lector_repository = AsyncMock(spec=LectorRepository)
    mock_center_repository = AsyncMock(spec=CenterRepository)
    mock_user_repository.exist_by_nickname.side_effect = [True]

    # when
    user_service = UserService(mock_user_repository, mock_lector_repository, mock_center_repository)
    result = await user_service.check_nickname_duplication(session, "existing_nickname")

    # then
    assert result.is_duplicated is True
