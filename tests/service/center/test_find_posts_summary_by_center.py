import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import UnauthorizedException, ErrorCode, NotFoundException
from claon_admin.model.auth import RequestUser
from claon_admin.schema.center import Center, Post
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for find posts summary by center")
class TestFindPostsSummaryByCenter(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_find_posts_summary_by_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            yesterday_post_fixture: Post,
            other_post_fixture: Post,
            another_post_fixture: Post,
            post_fixture: Post
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["post"].find_posts_summary_by_center.side_effect = [
            {
                "today": 1,
                "week": 2,
                "month": 2,
                "total": 4,
                "per_day": [(yesterday_post_fixture.id, yesterday_post_fixture.created_at)],
                "per_week": [(post_fixture.id, post_fixture.created_at),
                             (other_post_fixture.id, other_post_fixture.created_at),
                             (another_post_fixture.id, another_post_fixture.created_at),
                             (yesterday_post_fixture.id, yesterday_post_fixture.created_at)]
            }
        ]

        # when
        results = await center_service.find_posts_summary_by_center(None,
                                                                    request_user,
                                                                    center_fixture.id)

        # then
        assert results.center_id == center_fixture.id
        assert results.center_name == center_fixture.name
        assert results.count_today == 1
        assert results.count_week == 2
        assert results.count_month == 2
        assert results.count_total == 4
        assert len(results.count_per_day) == 7
        assert results.count_per_day[5].count == 0
        assert results.count_per_day[6].count == 1

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_find_posts_summary_by_center_with_not_exist_center(
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
            await center_service.find_posts_summary_by_center(None, request_user, wrong_id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request user is not center admin")
    async def test_find_posts_summary_by_center_with_not_center_admin(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.find_posts_summary_by_center(None, request_user, center_fixture.id)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
