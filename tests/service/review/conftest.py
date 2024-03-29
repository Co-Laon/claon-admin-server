import uuid
from datetime import datetime, timedelta
from typing import List
from unittest.mock import AsyncMock

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.util.time import now
from claon_admin.schema.center import CenterRepository, ReviewRepository, ReviewAnswerRepository, Center, CenterImage, \
    OperatingTime, Utility, CenterFeeImage, ReviewAnswer, Review, ReviewTag
from claon_admin.schema.post import Post, PostImage
from claon_admin.schema.user import User
from claon_admin.service.review import ReviewService


@pytest.fixture
def mock_repo():
    center_repository = AsyncMock(spec=CenterRepository)
    review_repository = AsyncMock(spec=ReviewRepository)
    review_answer_repository = AsyncMock(spec=ReviewAnswerRepository)

    return {
        "center": center_repository,
        "review": review_repository,
        "review_answer": review_answer_repository
    }


@pytest.fixture
def review_service(mock_repo: dict):
    return ReviewService(
        center_repository=mock_repo["center"],
        review_repository=mock_repo["review"],
        review_answer_repository=mock_repo["review_answer"]
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
def review_user_list_fixture():
    yield [
        User(
            id=str(uuid.uuid4()),
            oauth_id="r1_oauth_id",
            nickname="r1_nickname",
            profile_img="r1_profile_img",
            sns="r1_sns",
            email="r1_test@test.com",
            instagram_name="r1_instagram_name",
            role=Role.USER
        ),
        User(
            id=str(uuid.uuid4()),
            oauth_id="r2_oauth_id",
            nickname="r2_nickname",
            profile_img="r2_profile_img",
            sns="r2_sns",
            email="r2_test@test.com",
            instagram_name="r2_instagram_name",
            role=Role.USER
        ),
        User(
            id=str(uuid.uuid4()),
            oauth_id="r3_oauth_id",
            nickname="r3_nickname",
            profile_img="r3_profile_img",
            sns="r3_sns",
            email="r3_test@test.com",
            instagram_name="r3_instagram_name",
            role=Role.USER
        ),
        User(
            id=str(uuid.uuid4()),
            oauth_id="r4_oauth_id",
            nickname="r4_nickname",
            profile_img="r4_profile_img",
            sns="r4_sns",
            email="r4_test@test.com",
            instagram_name="r4_instagram_name",
            role=Role.USER
        )
    ]


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
def review_fixture(user_fixture: User, center_fixture: Center, review_answer_fixture: ReviewAnswer):
    yield Review(
        id=str(uuid.uuid4()),
        user=user_fixture,
        center=center_fixture,
        answer_id=review_answer_fixture.id,
        answer=review_answer_fixture,
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
def another_review_fixture(review_user_fixture: User, center_fixture: Center, another_review_answer_fixture: ReviewAnswer):
    yield Review(
        id=str(uuid.uuid4()),
        user=review_user_fixture,
        center=center_fixture,
        answer_id=another_review_answer_fixture.id,
        answer=another_review_answer_fixture,
        content="content",
        created_at=datetime(2023, 2, 5),
        tag=[ReviewTag(word="other_tag")]
    )


@pytest.fixture
def review_answer_fixture():
    yield ReviewAnswer(
        id=str(uuid.uuid4()),
        content="answer",
        created_at=datetime(2023, 2, 7)
    )


@pytest.fixture
def another_review_answer_fixture():
    yield ReviewAnswer(
        id=str(uuid.uuid4()),
        content="answer",
        created_at=datetime(2023, 2, 7)
    )


@pytest.fixture
def new_review_answer_fixture(review_fixture: Review):
    yield ReviewAnswer(
        id=str(uuid.uuid4()),
        content="new answer",
        review=review_fixture,
        created_at=datetime(2023, 2, 7)
    )


@pytest.fixture
def review_answer_list_fixture():
    yield [
        ReviewAnswer(
            id=str(uuid.uuid4()),
            content="answer1",
            created_at=now().date() - timedelta(days=1)
        ),
        ReviewAnswer(
            id=str(uuid.uuid4()),
            content="answer2",
            created_at=now().date() - timedelta(days=1)
        ),
        ReviewAnswer(
            id=str(uuid.uuid4()),
            content="answer3",
            created_at=now().date() - timedelta(days=1)
        )
    ]


@pytest.fixture
def review_list_fixture(
        review_answer_list_fixture: List[ReviewAnswer],
        review_user_list_fixture: List[User],
        center_fixture: Center
):
    yield [
        Review(
            id=str(uuid.uuid4()),
            user=review_user_list_fixture[0],
            center=center_fixture,
            answer_id=review_answer_list_fixture[0].id,
            answer=review_answer_list_fixture[0],
            content="content",
            created_at=datetime(2023, 4, 4),
            tag=[ReviewTag(word="tag"), ReviewTag(word="tag2")]
        ),
        Review(
            id=str(uuid.uuid4()),
            user=review_user_list_fixture[1],
            center=center_fixture,
            answer_id=review_answer_list_fixture[1].id,
            answer=review_answer_list_fixture[1],
            content="content",
            created_at=datetime(2023, 4, 4),
            tag=[ReviewTag(word="tag")]
        ),
        Review(
            id=str(uuid.uuid4()),
            user=review_user_list_fixture[2],
            center=center_fixture,
            answer_id=review_answer_list_fixture[2].id,
            answer=review_answer_list_fixture[2],
            content="content",
            created_at=datetime(2023, 4, 4),
            tag=[ReviewTag(word="tag2"), ReviewTag(word="tag3")]
        ),
        Review(
            id=str(uuid.uuid4()),
            user=review_user_list_fixture[3],
            center=center_fixture,
            answer_id=None,
            answer=None,
            content="content",
            created_at=datetime(2023, 4, 4),
            tag=[ReviewTag(word="tag"), ReviewTag(word="tag3")]
        )
    ]
