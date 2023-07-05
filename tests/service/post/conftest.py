import uuid
from datetime import datetime, timedelta
from typing import List
from unittest.mock import AsyncMock

import pytest

from claon_admin.common.enum import Role, WallType
from claon_admin.common.util.time import now
from claon_admin.schema.center import CenterRepository, Center, CenterImage, OperatingTime, Utility, CenterFeeImage, \
    CenterFee, CenterHold, CenterWall
from claon_admin.schema.post import PostRepository, Post, PostImage, ClimbingHistory, PostCountHistoryRepository, \
    PostCountHistory
from claon_admin.schema.user import User
from claon_admin.service.post import PostService


@pytest.fixture
def mock_repo():
    center_repository = AsyncMock(spec=CenterRepository)
    post_repository = AsyncMock(spec=PostRepository)
    post_count_history_repository = AsyncMock(spec=PostCountHistoryRepository)

    return {
        "center": center_repository,
        "post": post_repository,
        "post_count_history": post_count_history_repository
    }


@pytest.fixture
def post_service(mock_repo: dict):
    return PostService(
        center_repository=mock_repo["center"],
        post_repository=mock_repo["post"],
        post_count_history_repository=mock_repo["post_count_history"]
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
def center_fees_fixture(center_fixture: Center):
    yield [
        CenterFee(
            id=str(uuid.uuid4()),
            center=center_fixture,
            name="fee",
            price=1000,
            count=10
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
def post_fixture(user_fixture: User, center_fixture: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=user_fixture,
        center=center_fixture,
        content="content",
        created_at=datetime(2023, 2, 3),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def other_post_fixture(pending_user_fixture: User, center_fixture: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=pending_user_fixture,
        center=center_fixture,
        content="content",
        created_at=datetime(2023, 2, 3),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def another_post_fixture(user_fixture: User, center_fixture: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=user_fixture,
        center=center_fixture,
        content="content",
        created_at=datetime(2023, 2, 3),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def yesterday_post_fixture(user_fixture: User, center_fixture: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=user_fixture,
        center=center_fixture,
        content="content",
        created_at=now() - timedelta(days=1),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def today_post_fixture(user_fixture: User, center_fixture: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=user_fixture,
        center=center_fixture,
        content="content",
        created_at=now(),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
async def post_count_history_list_fixture(center_fixture: Center):
    yield [
        PostCountHistory(
            id=0,
            center_id=center_fixture.id,
            count=10,
            reg_date=now().date() - timedelta(weeks=52)
        ),
        PostCountHistory(
            id=1,
            center_id=center_fixture.id,
            count=10,
            reg_date=now().date() - timedelta(weeks=4)
        ),
        PostCountHistory(
            id=2,
            center_id=center_fixture.id,
            count=10,
            reg_date=now().date() - timedelta(weeks=1, days=1)
        ),
        PostCountHistory(
            id=3,
            center_id=center_fixture.id,
            count=10,
            reg_date=now().date() - timedelta(days=1)
        )
    ]


@pytest.fixture
def climbing_history_fixture(post_fixture: Post,
                             center_holds_fixture: List[CenterHold],
                             center_walls_fixture: List[CenterWall]):
    yield [
        ClimbingHistory(
            id=str(uuid.uuid4()),
            post=post_fixture,
            hold_id=center_holds_fixture[0].id,
            difficulty=center_holds_fixture[0].difficulty,
            challenge_count=3,
            wall_name=center_walls_fixture[0].name,
            wall_type=center_walls_fixture[0].type)
    ]
