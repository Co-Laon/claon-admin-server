from typing import List

import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.model.review import ReviewTagDto
from claon_admin.schema.center import Center, Review, ReviewAnswer
from claon_admin.schema.user import User
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for find reviews summary by center")
class TestFindReviewsSummaryByCenter(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_find_reviews_summary_by_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            review_user_list_fixture: List[User],
            review_list_fixture: List[Review],
            review_answer_list_fixture: List[ReviewAnswer]
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["review"].find_all_by_center.side_effect = [review_list_fixture]
        # when
        results = await center_service.find_reviews_summary_by_center(request_user, center_fixture.id)

        # then
        assert results.center_id == center_fixture.id
        assert results.center_name == center_fixture.name
        assert results.count_total == 4
        assert results.count_answered == 3
        assert results.count_not_answered == 1
        assert results.count_by_tag == [ReviewTagDto(tag="tag", count=3),
                                        ReviewTagDto(tag="tag2", count=2),
                                        ReviewTagDto(tag="tag3", count=2)]

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_find_reviews_summary_by_center_with_not_exist_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [None]
        wrong_id = "wrong id"

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.find_reviews_summary_by_center(request_user, wrong_id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request user is not center admin")
    async def test_find_reviews_summary_by_center_with_not_center_admin(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id="wrong id", sns="test@claon.com", role=Role.USER)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.find_reviews_summary_by_center(request_user, center_fixture.id)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
