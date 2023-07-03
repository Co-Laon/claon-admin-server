import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.schema.center import Center, Review, ReviewAnswer
from claon_admin.service.review import ReviewService


@pytest.mark.describe("Test case for delete review answer")
class TestDeleteReviewAnswer(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_delete_review_answer(
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
        mock_repo["review_answer"].find_by_review_id.side_effect = [review_answer_fixture]
        mock_repo["review_answer"].delete.side_effect = [review_answer_fixture]

        # when
        result = await review_service.delete_review_answer(
            request_user,
            center_fixture.id,
            review_fixture.id
        )

        # then
        assert result is review_answer_fixture

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_delete_review_answer_with_not_exist_center(
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

        with pytest.raises(NotFoundException) as exception:
            # when
            await review_service.delete_review_answer(request_user, wrong_id, review_fixture.id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request user is not center admin")
    async def test_delete_review_answer_with_not_center_admin(
            self,
            review_service: ReviewService,
            mock_repo: dict,
            center_fixture: Center,
            review_fixture: Review
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await review_service.delete_review_answer(request_user, center_fixture.id, review_fixture.id)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: review is not found")
    async def test_delete_review_answer_with_not_exist_review(
            self,
            review_service: ReviewService,
            mock_repo: dict,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["review"].find_by_id_and_center_id.side_effect = [None]
        wrong_review_id = "wrong id"

        with pytest.raises(NotFoundException) as exception:
            # when
            await review_service.delete_review_answer(request_user, center_fixture.id, wrong_review_id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: review answer is not found")
    async def test_delete_review_answer_with_not_exist_answer(
            self,
            review_service: ReviewService,
            mock_repo: dict,
            center_fixture: Center,
            review_fixture: Review
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["review"].find_by_id_and_center_id.side_effect = [review_fixture]
        mock_repo["review_answer"].find_by_review_id.side_effect = [None]

        with pytest.raises(NotFoundException) as exception:
            # when
            await review_service.delete_review_answer(request_user, center_fixture.id, review_fixture.id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST
