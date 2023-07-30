import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.model.review import ReviewAnswerRequestDto
from claon_admin.schema.center import Center, Review, ReviewAnswer
from claon_admin.service.review import ReviewService


@pytest.mark.describe("Test case for create review answer")
class TestCreateReviewAnswer(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_create_review_answer(
            self,
            review_service: ReviewService,
            mock_repo: dict,
            center_fixture: Center,
            not_answered_review_fixture: Review,
            new_review_answer_fixture: ReviewAnswer
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        dto = ReviewAnswerRequestDto(answer_content="new answer")

        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["review"].find_by_id_and_center_id.side_effect = [not_answered_review_fixture]
        mock_repo["review_answer"].save.side_effect = [new_review_answer_fixture]

        # when
        result = await review_service.create_review_answer(request_user, center_fixture.id, not_answered_review_fixture.id, dto)

        # then
        assert result.review_answer_id == new_review_answer_fixture.id

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_create_review_answer_with_not_exist_center(
            self,
            review_service: ReviewService,
            mock_repo: dict,
            center_fixture: Center,
            review_fixture: Review
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [None]
        wrong_id = "wrong id"
        dto = ReviewAnswerRequestDto(answer_content="content")

        with pytest.raises(NotFoundException) as exception:
            # when
            await review_service.create_review_answer(request_user, wrong_id, review_fixture.id, dto)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request user is not center admin")
    async def test_create_review_answer_with_not_center_admin(
            self,
            review_service: ReviewService,
            mock_repo: dict,
            center_fixture: Center,
            review_fixture: Review
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        dto = ReviewAnswerRequestDto(answer_content="content")

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await review_service.create_review_answer(request_user, center_fixture.id, review_fixture.id, dto)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: review is not found")
    async def test_create_review_answer_with_not_exist_review(
            self,
            review_service: ReviewService,
            mock_repo: dict,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["review"].find_by_id_and_center_id.side_effect = [None]
        dto = ReviewAnswerRequestDto(answer_content="content")
        wrong_review_id = "wrong id"

        with pytest.raises(NotFoundException) as exception:
            # when
            await review_service.create_review_answer(request_user, center_fixture.id, wrong_review_id, dto)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: review is already answered")
    async def test_create_review_answer_with_already_exist_answer(
            self,
            review_service: ReviewService,
            mock_repo: dict,
            center_fixture: Center,
            review_fixture: Review,
            review_answer_fixture: ReviewAnswer
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["review"].find_by_id_and_center_id.side_effect = [review_fixture]
        dto = ReviewAnswerRequestDto(answer_content="content")

        with pytest.raises(NotFoundException) as exception:
            # when
            await review_service.create_review_answer(request_user, center_fixture.id, review_fixture.id, dto)

        # then
        assert exception.value.code == ErrorCode.ROW_ALREADY_EXIST
