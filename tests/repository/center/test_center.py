import pytest
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.schema.center import Center
from claon_admin.schema.user import User
from tests.repository.center.conftest import center_repository, center_hold_repository, center_wall_repository, \
    center_fee_repository, center_approved_file_repository


@pytest.mark.describe("Test case for center repository")
class TestCenterRepository(object):
    @pytest.mark.asyncio
    async def test_save_center(
            self,
            session: AsyncSession,
            user_fixture: User,
            center_fixture: Center
    ):
        # then
        assert center_fixture.user.id == user_fixture.id
        assert center_fixture.user == user_fixture
        assert center_fixture.name == "test center"
        assert center_fixture.profile_img == "https://test.profile.png"
        assert center_fixture.address == "test_address"
        assert center_fixture.detail_address == "test_detail_address"
        assert center_fixture.tel == "010-1234-5678"
        assert center_fixture.web_url == "http://test.com"
        assert center_fixture.instagram_name == "test_instagram"
        assert center_fixture.youtube_url == "https://www.youtube.com/@test"
        assert center_fixture.center_img[0].url == "https://test.image.png"
        assert center_fixture.operating_time[0].day_of_week == "월"
        assert center_fixture.operating_time[0].start_time == "09:00"
        assert center_fixture.operating_time[0].end_time == "18:00"
        assert center_fixture.utility[0].name == "test_utility"
        assert center_fixture.fee_img[0].url == "https://test.fee.png"
        assert center_fixture.approved is True

    @pytest.mark.asyncio
    async def test_find_center_by_id(
            self,
            session: AsyncSession,
            center_fixture: Center
    ):
        # given
        center_id = center_fixture.id

        # when
        result = await center_repository.find_by_id(session, center_id)

        # then
        assert result == center_fixture

    @pytest.mark.asyncio
    async def test_find_center_by_non_existing_id(
            self,
            session: AsyncSession,
    ):
        # given
        center_id = "non_existing_id"

        # when
        result = await center_repository.find_by_id(session, center_id)

        # then
        assert result is None

    @pytest.mark.asyncio
    async def test_find_center_by_id_with(
            self,
            session: AsyncSession,
            center_fixture: Center
    ):
        # given
        center_id = center_fixture.id

        # when
        result = await center_repository.find_by_id_with_details(session, center_id)

        # then
        assert result == center_fixture
        assert result.user == center_fixture.user

    @pytest.mark.asyncio
    async def test_find_center_by_non_existing_id_with(
            self,
            session: AsyncSession,
    ):
        # given
        center_id = "non_existing_id"

        # when
        result = await center_repository.find_by_id_with_details(session, center_id)

        # then
        assert result is None

    @pytest.mark.asyncio
    async def test_approve_center(
            self,
            session: AsyncSession,
            center_fixture: Center
    ):
        # when
        result = await center_repository.approve(session, center_fixture)

        # then
        assert result.approved is True

    @pytest.mark.asyncio
    async def test_delete_center(
            self,
            session: AsyncSession,
            center_fixture: Center
    ):
        # when
        await center_repository.delete(session, center_fixture)

        # then
        assert await center_repository.find_by_id_with_details(session, center_fixture.id) is None
        assert await center_hold_repository.find_all_by_center_id(session, center_fixture.id) == []
        assert await center_wall_repository.find_all_by_center_id(session, center_fixture.id) == []
        assert await center_fee_repository.find_all_by_center_id(session, center_fixture.id) == []
        assert await center_approved_file_repository.find_all_by_center_id(session, center_fixture.id) == []

    @pytest.mark.asyncio
    async def test_find_all_center_by_approved_false(
            self,
            session: AsyncSession,
            center_fixture: Center
    ):
        # given
        center_fixture.approved = False

        # when
        result = await center_repository.find_all_by_approved_false(session)

        # then
        assert result == [center_fixture]

    @pytest.mark.asyncio
    async def test_find_centers_by_name(
            self,
            session: AsyncSession,
            center_fixture: Center,
            another_center_fixture: Center
    ):
        # when
        result = await center_repository.find_by_name(session, center_fixture.name)

        # then
        assert result == [another_center_fixture]

    @pytest.mark.asyncio
    async def test_find_centers(
            self,
            session: AsyncSession,
            user_fixture: User,
            center_fixture: Center,
            another_center_fixture: Center
    ):
        # given
        params = Params(page=1, size=10)

        # then
        assert await center_repository.find_all_by_user_id(
            session, user_fixture.id, params
        ) == Page.create(items=[center_fixture], params=params, total=1)

    @pytest.mark.asyncio
    async def test_find_all_ids_by_approved_true(
            self,
            session: AsyncSession,
            center_fixture: Center
    ):
        # then
        assert await center_repository.find_all_ids_by_approved_true(session) == [center_fixture.id]

    @pytest.mark.asyncio
    async def test_remove_center(
            self,
            session: AsyncSession,
            center_fixture: Center
    ):
        # then
        result = await center_repository.remove_center(session, center_fixture)
        assert result.user_id is None

    # @pytest.mark.asyncio
    # async def test_update(
    #         self,
    #         session: AsyncSession,
    #         center_fixture: Center,
    # ):
    #     # given
    #     # {'profile_image': 'string', 'tel': '010-3392-5969', 'web_url': 'string', 'instagram_name': 'string', 'youtube_code': '@string', 'image_list': ['string'], 'utility_list': ['string'], 'fee_image_list': ['string'], 'operating_time_list': [CenterOperatingTimeDto(day_of_week='월', start_time='12:00', end_time='01:00')], 'fee_list': [CenterFeeDto(name='string', price=0, count=0)], 'hold_list': [CenterHoldDto(difficulty='string', name='string', is_color=True)], 'wall_list': [CenterWallDto(wall_type=<WallType.ENDURANCE: 'endurance'>, name='string')]}
        
    #     request = { # 이쪽 dict 안에 dto가 들어가서 생기는 문제 
    #         "profile_image": "string",
    #         "tel": "010-1234-1234",
    #         "web_url": "string",
    #         "instagram_name": "string",
    #         "youtube_code": "@string",
    #         "image_list": ["string"],
    #         "utility_list": ["string"],
    #         "fee_image_list": ["string"],
    #         "operating_time_list": [{"day_of_week": "월", "start_time": "12:00", "end_time": "01:00"}],
    #         "fee_list": [{"name": "string", "price": 0, "count": 0}],
    #         "hold_list": [{"difficulty": "string", "name": "string", "is_color": True}],
    #         "wall_list": [{"wall_type": "endurance", "name": "string"}]
    #     }

    #     # when
    #     result = await center_repository.update(session, center_fixture, request)
        
    #     # then
    #     print("LOG:", request)
    #     assert result.profile_img == request['profile_image']
    #     assert result.tel == request['tel']
    #     assert result.web_url == request['web_url']
    #     assert result.instagram_name == request['instagram_name']
    #     assert result.youtube_url == f"https://www.youtube.com/{str(request['youtube_code'])}"
    #     assert result.center_img[0].url == request['image_list'][0]
    #     assert result.operating_time[0].day_of_week == request['operating_time_list'][0]['day_of_week']
    #     assert result.operating_time[0].start_time == request['operating_time_list'][0]['start_time']
    #     assert result.operating_time[0].end_time == request['operating_time_list'][0]['end_time']
    #     assert result.utility[0].name == request['utility_list'][0]
    #     assert result.fee_img[0].url == request['fee_image_list'][0]
