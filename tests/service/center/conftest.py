import uuid
from datetime import datetime, timedelta
from typing import List
from unittest.mock import AsyncMock

import pytest

from claon_admin.common.enum import Role, WallType
from claon_admin.common.util.pagination import PaginationFactory
from claon_admin.common.util.time import now
from claon_admin.schema.center import CenterRepository, PostRepository, ReviewRepository, ReviewAnswerRepository, \
    Center, CenterImage, OperatingTime, Utility, CenterFeeImage, CenterHold, CenterWall, Post, PostImage, \
    ClimbingHistory, Review, ReviewTag, ReviewAnswer
from claon_admin.schema.user import User
from claon_admin.service.center import CenterService


@pytest.fixture
def mock_repo():
    center_repository = AsyncMock(spec=CenterRepository)
    post_repository = AsyncMock(spec=PostRepository)
    review_repository = AsyncMock(spec=ReviewRepository)
    review_answer_repository = AsyncMock(spec=ReviewAnswerRepository)
    pagination_factory = AsyncMock(spec=PaginationFactory)

    return {
        "center": center_repository,
        "post": post_repository,
        "review": review_repository,
        "review_answer": review_answer_repository,
        "pagination_factory": pagination_factory
    }


@pytest.fixture
def center_service(mock_repo: dict):
    return CenterService(
        mock_repo["center"],
        mock_repo["post"],
        mock_repo["review"],
        mock_repo["review_answer"],
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
        role=Role.CENTER_ADMIN
    )


@pytest.fixture
def mock_pending_user():
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
def mock_review_user():
    yield User(
        id=str(uuid.uuid4()),
        oauth_id="r_oauth_id",
        nickname="r_nickname",
        profile_img="r_profile_img",
        sns="r_sns",
        email="r_test@test.com",
        instagram_name="r_instagram_name",
        role=Role.USER
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
async def mock_center_walls(mock_center: Center):
    yield [
        CenterWall(
            id=str(uuid.uuid4()),
            center=mock_center,
            name="wall",
            type=WallType.ENDURANCE.value
        )
    ]


@pytest.fixture
def mock_post(mock_user: User, mock_center: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=mock_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 3),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def mock_other_post(mock_pending_user: User, mock_center: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=mock_pending_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 3),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def mock_another_post(mock_review_user: User, mock_center: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=mock_review_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 3),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def mock_yesterday_post(mock_user: User, mock_center: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=mock_user,
        center=mock_center,
        content="content",
        created_at=now() - timedelta(days=1),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def mock_today_post(mock_user: User, mock_center: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=mock_user,
        center=mock_center,
        content="content",
        created_at=now(),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def mock_climbing_history(mock_post: Post, mock_center_holds: List[CenterHold], mock_center_walls: List[CenterWall]):
    yield [
        ClimbingHistory(
            id=str(uuid.uuid4()),
            post=mock_post,
            hold_id=mock_center_holds[0].id,
            difficulty=mock_center_holds[0].difficulty,
            challenge_count=3,
            wall_name=mock_center_walls[0].name,
            wall_type=mock_center_walls[0].type)
    ]


@pytest.fixture
def mock_review(mock_user: User, mock_center: Center):
    yield Review(
        id=str(uuid.uuid4()),
        user=mock_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="tag")]
    )


@pytest.fixture
def mock_not_answered_review(mock_user: User, mock_center: Center):
    yield Review(
        id=str(uuid.uuid4()),
        user=mock_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="tag")]
    )


@pytest.fixture
def mock_other_review(mock_pending_user: User, mock_center: Center):
    yield Review(
        id=str(uuid.uuid4()),
        user=mock_pending_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="tag")]
    )


@pytest.fixture
def mock_another_review(mock_review_user: User, mock_center: Center):
    yield Review(
        id=str(uuid.uuid4()),
        user=mock_review_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="other_tag")]
    )


@pytest.fixture
def mock_review_answer(mock_review: Review):
    yield ReviewAnswer(
        id=str(uuid.uuid4()),
        review=mock_review,
        content="answer",
        created_at=datetime(2023, 2, 7)
    )


@pytest.fixture
def mock_another_review_answer(mock_another_review: Review):
    yield ReviewAnswer(
        id=str(uuid.uuid4()),
        review=mock_another_review,
        content="answer",
        created_at=datetime(2023, 2, 7)
    )


@pytest.fixture
def mock_new_review_answer(mock_not_answered_review: Review):
    yield ReviewAnswer(
        id=str(uuid.uuid4()),
        review=mock_not_answered_review,
        content="new answer",
        created_at=datetime(2023, 2, 7)
    )
