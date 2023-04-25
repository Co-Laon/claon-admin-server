import uuid
from datetime import date
from typing import List
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import BadRequestException
from claon_admin.model.auth import RequestUser
from claon_admin.model.enum import Role
from claon_admin.schema.center import CenterRepository, CenterApprovedFileRepository, Center, CenterApprovedFile, \
    CenterImage, OperatingTime, Utility, CenterFee, CenterFeeImage
from claon_admin.schema.user import LectorRepository, LectorApprovedFileRepository, Lector, LectorApprovedFile, User, \
    Contest, Certificate, Career, UserRepository
from claon_admin.service.admin import AdminService


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
        fee=[CenterFee(name="test_fee_name", price=1000, count=10)],
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


@pytest.mark.asyncio
@patch("claon_admin.service.admin.delete_file")
async def test_approve_center(
        mock_delete_file,
        session: AsyncSession,
        mock_repo: dict,
        admin_service: AdminService,
        mock_center: Center,
        mock_center_approved_files: List[CenterApprovedFile]
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.ADMIN)
    center_id = mock_center.id

    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_center.approved = True
    mock_repo["center"].approve.side_effect = [mock_center]
    mock_center.user.role = Role.CENTER_ADMIN
    mock_repo["user"].update_role.side_effect = [mock_center.user]
    mock_repo["center_approved_file"].find_all_by_center_id.side_effect = [mock_center_approved_files]
    mock_delete_file.return_value = None

    # when
    result = await admin_service.approve_center(session, request_user, center_id)

    # then
    assert result.approved
    assert result.user_profile.role == Role.CENTER_ADMIN


@pytest.mark.asyncio
async def test_approve_center_with_non_admin(
        session: AsyncSession,
        mock_repo: dict,
        admin_service: AdminService,
        mock_center: Center
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.PENDING)
    center_id = mock_center.id

    # then
    with pytest.raises(BadRequestException):
        # when
        await admin_service.approve_center(session, request_user, center_id)


@pytest.mark.asyncio
async def test_approve_not_existing_center(
        session: AsyncSession,
        mock_repo: dict,
        admin_service: AdminService
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.ADMIN)
    center_id = "not_existing_id"

    mock_repo["center"].find_by_id.side_effect = [None]

    # then
    with pytest.raises(BadRequestException):
        # when
        await admin_service.approve_center(session, request_user, center_id)


@pytest.mark.asyncio
@patch("claon_admin.service.admin.delete_file")
async def test_approve_lector(
        mock_delete_file,
        session: AsyncSession,
        mock_repo: dict,
        admin_service: AdminService,
        mock_lector: Lector,
        mock_lector_approved_files: List[LectorApprovedFile]
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.ADMIN)
    lector_id = mock_lector.id

    mock_repo["lector"].find_by_id.side_effect = [mock_lector]
    mock_lector.approved = True
    mock_repo["lector"].approve.side_effect = [mock_lector]
    mock_lector.user.role = Role.LECTOR
    mock_repo["user"].update_role.side_effect = [mock_lector.user]
    mock_repo["lector_approved_file"].find_all_by_lector_id.side_effect = [mock_lector_approved_files]
    mock_delete_file.return_value = None

    # when
    result = await admin_service.approve_lector(session, request_user, lector_id)

    # then
    assert result.approved
    assert result.user_profile.role == Role.LECTOR


@pytest.mark.asyncio
async def test_approve_lector_with_non_admin(
        session: AsyncSession,
        mock_repo: dict,
        admin_service: AdminService,
        mock_lector: Lector
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.PENDING)
    lector_id = mock_lector.id

    # then
    with pytest.raises(BadRequestException):
        # when
        await admin_service.approve_lector(session, request_user, lector_id)


@pytest.mark.asyncio
async def test_approve_not_existing_lector(
        session: AsyncSession,
        mock_repo: dict,
        admin_service: AdminService,
        mock_lector: Lector
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.ADMIN)
    lector_id = "not_existing_id"

    mock_repo["lector"].find_by_id.side_effect = [None]

    # then
    with pytest.raises(BadRequestException):
        # when
        await admin_service.approve_lector(session, request_user, lector_id)


@pytest.mark.asyncio
async def test_reject_center(
        session: AsyncSession,
        mock_repo: dict,
        admin_service: AdminService,
        mock_center: Center
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.ADMIN)
    center_id = mock_center.id

    mock_repo["center"].find_by_id.side_effect = [mock_center]

    # when
    result = await admin_service.reject_center(session, request_user, center_id)

    # then
    assert result is None


@pytest.mark.asyncio
async def test_reject_center_with_non_admin(
        session: AsyncSession,
        mock_repo: dict,
        admin_service: AdminService,
        mock_center: Center
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.PENDING)
    center_id = mock_center.id

    # then
    with pytest.raises(BadRequestException):
        # when
        await admin_service.reject_center(session, request_user, center_id)


@pytest.mark.asyncio
async def test_reject_not_existing_center(
        session: AsyncSession,
        mock_repo: dict,
        admin_service: AdminService
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.PENDING)
    center_id = "not_existing_id"

    mock_repo["center"].find_by_id.side_effect = [None]

    # then
    with pytest.raises(BadRequestException):
        # when
        await admin_service.reject_center(session, request_user, center_id)


@pytest.mark.asyncio
async def test_reject_lector(
        session: AsyncSession,
        mock_repo: dict,
        admin_service: AdminService,
        mock_lector: Lector
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.ADMIN)
    lector_id = mock_lector.id

    mock_repo["lector"].find_by_id.side_effect = [mock_lector]
    mock_repo["lector"].delete.side_effect = [mock_lector]

    # when
    result = await admin_service.reject_lector(session, request_user, lector_id)

    # then
    assert result is mock_lector


@pytest.mark.asyncio
async def test_reject_lector_with_non_admin(
        session: AsyncSession,
        mock_repo: dict,
        admin_service: AdminService,
        mock_lector: Lector
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.PENDING)
    lector_id = mock_lector.id

    # then
    with pytest.raises(BadRequestException):
        # when
        await admin_service.reject_lector(session, request_user, lector_id)


@pytest.mark.asyncio
async def test_reject_not_existing_lector(
        session: AsyncSession,
        mock_repo: dict,
        admin_service: AdminService
):
    # given
    request_user = RequestUser(id="123456", email="test@claon.com", role=Role.PENDING)
    lector_id = "not_existing_id"

    mock_repo["lector"].find_by_id.side_effect = [None]

    # then
    with pytest.raises(BadRequestException):
        # when
        await admin_service.reject_lector(session, request_user, lector_id)
