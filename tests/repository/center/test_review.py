from datetime import datetime

import pytest
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.center import Center, Review, ReviewAnswer, Post
from claon_admin.schema.user import User
from tests.repository.center.conftest import review_repository, review_answer_repository


@pytest.mark.describe("Test case for review repository")
class TestReviewRepository(object):
    @pytest.mark.asyncio
    async def test_save_review(
            self,
            session: AsyncSession,
            user_fixture: User,
            center_fixture: Center,
            review_fixture: Review
    ):
        assert review_fixture.user == user_fixture
        assert review_fixture.center == center_fixture
        assert review_fixture.content == "content"
        assert review_fixture.tag[0].word == "tag"
        assert review_fixture.created_at == datetime(2023, 1, 1)

    @pytest.mark.asyncio
    async def test_find_reviews_by_center_not_filter(
            self,
            session: AsyncSession,
            center_fixture: Center,
            review_fixture: Review,
            post_fixture: Post,
            review_answer_fixture: ReviewAnswer
    ):
        # given
        params = Params(page=1, size=10)

        # then
        assert await review_repository.find_reviews_by_center(
            session=session,
            params=params,
            center_id=center_fixture.id,
            start=datetime(2022, 3, 1),
            end=datetime(2023, 2, 28),
            tag=None,
            is_answered=None
        ) == Page.create(items=[(review_fixture, 1)], params=params, total=1)

    @pytest.mark.asyncio
    async def test_find_reviews_by_center_with_tag(
            self,
            session: AsyncSession,
            center_fixture: Center,
            review_fixture: Review,
            post_fixture: Post,
            review_answer_fixture: ReviewAnswer
    ):
        # given
        params = Params(page=1, size=10)

        # then
        assert await review_repository.find_reviews_by_center(
            session=session,
            params=params,
            center_id=center_fixture.id,
            start=datetime(2022, 3, 1),
            end=datetime(2023, 2, 28),
            tag="tag",
            is_answered=None
        ) == Page.create(items=[(review_fixture, 1)], params=params, total=1)

    @pytest.mark.asyncio
    async def test_find_reviews_with_by_center_only_not_answered(
            self,
            session: AsyncSession,
            center_fixture: Center,
            review_fixture: Review,
            post_fixture: Post,
            review_answer_fixture: ReviewAnswer
    ):
        # given
        params = Params(page=1, size=10)

        # then
        assert await review_repository.find_reviews_by_center(
            session=session,
            params=params,
            center_id=center_fixture.id,
            start=datetime(2022, 3, 1),
            end=datetime(2023, 2, 28),
            tag=None,
            is_answered=False
        ) == Page.create(items=[], params=params, total=0)

    @pytest.mark.asyncio
    async def test_find_review_by_id_and_center_id(
            self,
            session: AsyncSession,
            center_fixture: Center,
            review_fixture: Review
    ):
        # then
        assert await review_repository.find_by_id_and_center_id(
            session,
            review_fixture.id,
            center_fixture.id
        ) == review_fixture


@pytest.mark.describe("Test case for review answer repository")
class TestReviewAnswerRepository(object):
    @pytest.mark.asyncio
    async def test_save_review_answer(
            self,
            session: AsyncSession,
            review_fixture: Review,
            review_answer_fixture: ReviewAnswer
    ):
        assert review_answer_fixture.review == review_fixture
        assert review_answer_fixture.content == "content"
        assert review_answer_fixture.created_at == datetime(2023, 1, 2)

    @pytest.mark.asyncio
    async def test_update_review_answer(
            self,
            session: AsyncSession,
            review_answer_fixture: ReviewAnswer
    ):
        # when
        updated_answer = await review_answer_repository.update(
            session=session,
            answer=review_answer_fixture,
            content="updated answer"
        )

        # then
        assert review_answer_fixture.content == updated_answer.content

    @pytest.mark.asyncio
    async def test_delete_review_answer(
            self,
            session: AsyncSession,
            review_fixture: Review,
            review_answer_fixture: ReviewAnswer
    ):
        # when
        await review_answer_repository.delete(
            session=session,
            answer=review_answer_fixture
        )

        # then
        assert await review_answer_repository.find_by_review_id(session, review_fixture.id) is None
