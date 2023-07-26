import uuid
from datetime import date
from unittest.mock import AsyncMock

import pytest

from claon_admin.common.enum import Role, WallType
from claon_admin.service.oauth import OAuthUserInfoProviderSupplier
from claon_admin.schema.center import CenterRepository, CenterApprovedFileRepository, CenterHoldRepository, \
    CenterWallRepository, Center, CenterImage, OperatingTime, Utility, CenterApprovedFile, CenterHold, CenterWall
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
        mock_repo["center_hold"],
        mock_repo["center_wall"],
        mock_supplier
    )


@pytest.fixture
def user_fixture():
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
def other_user_fixture():
    yield User(
        id=str(uuid.uuid4()),
        oauth_id="other_oauth_id",
        nickname="other_nickname",
        profile_img="other_profile_img",
        sns="other_sns",
        email="other_test@test.com",
        instagram_name="other_instagram_name",
        role=Role.USER
    )


@pytest.fixture
def lector_fixture(user_fixture: User):
    yield Lector(
        id=str(uuid.uuid4()),
        user=user_fixture,
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
def lector_approved_files_fixture(lector_fixture: Lector):
    yield LectorApprovedFile(
        id=str(uuid.uuid4()),
        lector=lector_fixture,
        url="https://test.com/test.pdf"
    )


@pytest.fixture
def center_fixture(user_fixture: User):
    yield Center(
        id=str(uuid.uuid4()),
        user=user_fixture,
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
        approved=False
    )


@pytest.fixture
def other_center_fixture(user_fixture: User):
    yield Center(
        id=str(uuid.uuid4()),
        user=user_fixture,
        name="test other center",
        profile_img="https://test.other.profile.png",
        address="test_other_address",
        detail_address="test_other_detail_address",
        tel="010-2222-2222",
        web_url="http://test.other.com",
        instagram_name="test_other_instagram",
        youtube_url="https://www.youtube.com/@othertest",
        center_img=[CenterImage(url="https://test.other.image.png")],
        operating_time=[OperatingTime(day_of_week="금", start_time="10:00", end_time="18:00")],
        utility=[Utility(name="test_other_utility")],
        approved=True
    )


@pytest.fixture
def center_approved_files_fixture(user_fixture: User, center_fixture: Center):
    yield [
        CenterApprovedFile(
            id=str(uuid.uuid4()),
            user=user_fixture,
            center=center_fixture,
            url="https://example.com/approved.jpg"
        )
    ]


@pytest.fixture
def center_holds_fixture(center_fixture: Center):
    yield [
        CenterHold(
            id=str(uuid.uuid4()),
            center=center_fixture,
            name="hold",
            difficulty="hard",
            is_color=False
        )
    ]


@pytest.fixture
def center_walls_fixture(center_fixture: Center):
    yield [
        CenterWall(
            id=str(uuid.uuid4()),
            center=center_fixture,
            name="wall",
            type=WallType.ENDURANCE.value
        )
    ]
