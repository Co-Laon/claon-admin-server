import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from claon_admin.common.enum import Role, WallType, CenterFeeType, PeriodType
from claon_admin.schema.center import CenterRepository, Center, CenterImage, OperatingTime, Utility, CenterFeeImage, \
    CenterFee, CenterHold, CenterWall, CenterHoldRepository, CenterWallRepository, CenterFeeRepository, \
    CenterApprovedFileRepository, CenterApprovedFile, CenterScheduleMemberRepository, CenterScheduleRepository, \
    CenterSchedule, CenterScheduleMember
from claon_admin.schema.user import User, UserRepository
from claon_admin.service.center import CenterService


@pytest.fixture
def mock_repo():
    user_repository = AsyncMock(spec=UserRepository)
    center_repository = AsyncMock(spec=CenterRepository)
    center_fee_repository = AsyncMock(spec=CenterFeeRepository)
    center_hold_repository = AsyncMock(spec=CenterHoldRepository)
    center_wall_repository = AsyncMock(spec=CenterWallRepository)
    center_approved_file_repository = AsyncMock(spec=CenterApprovedFileRepository)
    center_schedule_repository = AsyncMock(spec=CenterScheduleRepository)
    center_schedule_member_repository = AsyncMock(spec=CenterScheduleMemberRepository)

    return {
        "user": user_repository,
        "center": center_repository,
        "center_fee": center_fee_repository,
        "center_hold": center_hold_repository,
        "center_wall": center_wall_repository,
        "center_approved_file": center_approved_file_repository,
        "center_schedule": center_schedule_repository,
        "center_schedule_member": center_schedule_member_repository
    }


@pytest.fixture
def center_service(mock_repo: dict):
    return CenterService(
        user_repository=mock_repo["user"],
        center_repository=mock_repo["center"],
        center_hold_repository=mock_repo["center_hold"],
        center_wall_repository=mock_repo["center_wall"],
        center_fee_repository=mock_repo["center_fee"],
        center_approved_file_repository=mock_repo["center_approved_file"],
        center_schedule_repository=mock_repo["center_schedule"],
        center_schedule_member_repository=mock_repo["center_schedule_member"]
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
        role=Role.CENTER_ADMIN
    )


@pytest.fixture
def client_user_fixture():
    yield User(
        id=str(uuid.uuid4()),
        oauth_id="user_oauth_id",
        nickname="user_nickname",
        profile_img="user_profile_img",
        sns="user_sns",
        email="user_test@test.com",
        instagram_name="user_instagram_name",
        role=Role.USER
    )


@pytest.fixture
def pending_user_fixture():
    yield User(
        id=str(uuid.uuid4()),
        oauth_id="pending_oauth_id",
        nickname="pending_nickname",
        profile_img="pending_profile_img",
        sns="pending_sns",
        email="pending_test@test.com",
        instagram_name="pending_instagram_name",
        role=Role.PENDING
    )


@pytest.fixture
def center_fixture(user_fixture: User):
    yield Center(
        id=str(uuid.uuid4()),
        user=user_fixture,
        user_id=user_fixture.id,
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
def another_center_fixture(user_fixture: User):
    yield Center(
        id=str(uuid.uuid4()),
        user=user_fixture,
        name="other test center",
        profile_img="https://test.profile.png",
        address="other_test_address",
        detail_address="other_test_detail_address",
        tel="010-1234-5678",
        web_url="http://othertest.com",
        instagram_name="other_test_instagram",
        youtube_url="https://www.youtube.com/@othertest",
        center_img=[CenterImage(url="https://othertest.image.png")],
        operating_time=[OperatingTime(day_of_week="월", start_time="09:00", end_time="18:00")],
        utility=[Utility(name="test_utility")],
        fee_img=[CenterFeeImage(url="https://test.fee.png")],
        approved=False
    )


@pytest.fixture
def new_center_fixture(user_fixture: User):
    yield Center(
        id=str(uuid.uuid4()),
        user=user_fixture,
        name="test name",
        profile_img="https://test.profile.png",
        address="test_profile_image",
        detail_address="test_detail_address",
        tel="010-1111-1111",
        web_url="test_web_url",
        instagram_name="test_instagram_name",
        youtube_url="https://www.youtube.com/@testsave",
        center_img=[CenterImage(url="test_image")],
        operating_time=[OperatingTime(day_of_week="월", start_time="10:00", end_time="15:00")],
        utility=[Utility(name="test_utility")],
        fee_img=[CenterFeeImage(url="test_fee_image")],
        approved=False
    )


@pytest.fixture
def center_fees_fixture(center_fixture: Center):
    yield [
        CenterFee(
            id=str(uuid.uuid4()),
            center=center_fixture,
            name="fee",
            fee_type=CenterFeeType.PACKAGE,
            price=1000,
            count=10,
            period=1,
            period_type=PeriodType.DAY,
            is_deleted=False
        ),
        CenterFee(
            id=str(uuid.uuid4()),
            center=center_fixture,
            name="fee",
            fee_type=CenterFeeType.PACKAGE,
            price=1000,
            count=10,
            period=1,
            period_type=PeriodType.DAY,
            is_deleted=True
        )
    ]


@pytest.fixture
def new_center_fees_fixture(center_fixture: Center):
    yield CenterFee(
        id=str(uuid.uuid4()),
        center=center_fixture,
        name="new_fee",
        fee_type=CenterFeeType.PACKAGE,
        price=1000,
        count=10,
        period=1,
        period_type=PeriodType.DAY,
        is_deleted=False
    )


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
def new_center_holds_fixture(new_center_fixture: Center):
    yield [
        CenterHold(
            id=str(uuid.uuid4()),
            center=new_center_fixture,
            name="name",
            difficulty="red",
            is_color=True
        )
    ]


@pytest.fixture
async def center_walls_fixture(center_fixture: Center):
    yield [
        CenterWall(
            id=str(uuid.uuid4()),
            center=center_fixture,
            name="wall",
            type=WallType.ENDURANCE.value
        )
    ]


@pytest.fixture
async def new_center_walls_fixture(new_center_fixture: Center):
    yield [
        CenterWall(
            id=str(uuid.uuid4()),
            center=new_center_fixture,
            name="wall",
            type=WallType.BOULDERING.value
        )
    ]


@pytest.fixture
async def new_approved_file_fixture(user_fixture: User, new_center_fixture: Center):
    yield [
        CenterApprovedFile(
            id=str(uuid.uuid4()),
            user=user_fixture,
            center=new_center_fixture,
            url="url"
        )
    ]


@pytest.fixture
async def schedule_fixture(center_fixture: Center):
    yield CenterSchedule(
        id=str(uuid.uuid4()),
        title="schedule_title",
        start_time=datetime(2023, 8, 1, 10, 0),
        end_time=datetime(2023, 8, 2, 10, 0),
        description="test_description",
        center=center_fixture
    )


@pytest.fixture
async def new_schedule_fixture(center_fixture: Center):
    yield CenterSchedule(
        id=str(uuid.uuid4()),
        title="title",
        start_time=datetime(2023, 1, 1, 10, 0),
        end_time=datetime(2023, 1, 2, 10, 0),
        description="description",
        center=center_fixture
    )


@pytest.fixture
async def new_schedule_member_fixture(user_fixture: User, new_schedule_fixture: CenterSchedule):
    yield [
        CenterScheduleMember(
            id=str(uuid.uuid4()),
            user=user_fixture,
            schedule=new_schedule_fixture
        )
    ]
