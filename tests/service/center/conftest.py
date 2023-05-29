import uuid
from datetime import datetime, timedelta
from typing import List
from unittest.mock import AsyncMock

import pytest

from claon_admin.common.enum import Role, WallType
from claon_admin.common.util.pagination import PaginationFactory
from claon_admin.common.util.time import now
from claon_admin.schema.center import CenterRepository, ReviewRepository, ReviewAnswerRepository, Center, CenterImage, \
    OperatingTime, Utility, CenterFeeImage, CenterHold, CenterWall, Review, ReviewTag, ReviewAnswer
from claon_admin.schema.post import PostRepository, Post, PostImage, ClimbingHistory
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
def review_user_fixture():
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
def another_post_fixture(review_user_fixture: User, center_fixture: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=review_user_fixture,
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
def climbing_history_fixture(post_fixture: Post, center_holds_fixture: List[CenterHold],
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


@pytest.fixture
def review_fixture(user_fixture: User, center_fixture: Center):
    yield Review(
        id=str(uuid.uuid4()),
        user=user_fixture,
        center=center_fixture,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="tag")]
    )


@pytest.fixture
def not_answered_review_fixture(user_fixture: User, center_fixture: Center):
    yield Review(
        id=str(uuid.uuid4()),
        user=user_fixture,
        center=center_fixture,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="tag")]
    )


@pytest.fixture
def other_review_fixture(pending_user_fixture: User, center_fixture: Center):
    yield Review(
        id=str(uuid.uuid4()),
        user=pending_user_fixture,
        center=center_fixture,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="tag")]
    )


@pytest.fixture
def another_review_fixture(review_user_fixture: User, center_fixture: Center):
    yield Review(
        id=str(uuid.uuid4()),
        user=review_user_fixture,
        center=center_fixture,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="other_tag")]
    )


@pytest.fixture
def review_answer_fixture(review_fixture: Review):
    yield ReviewAnswer(
        id=str(uuid.uuid4()),
        review=review_fixture,
        content="answer",
        created_at=datetime(2023, 2, 7)
    )


@pytest.fixture
def another_review_answer_fixture(another_review_fixture: Review):
    yield ReviewAnswer(
        id=str(uuid.uuid4()),
        review=another_review_fixture,
        content="answer",
        created_at=datetime(2023, 2, 7)
    )


@pytest.fixture
def new_review_answer_fixture(not_answered_review_fixture: Review):
    yield ReviewAnswer(
        id=str(uuid.uuid4()),
        review=not_answered_review_fixture,
        content="new answer",
        created_at=datetime(2023, 2, 7)
    )
