from typing import List

import pytest

from claon_admin.common.enum import Role, WallType
from claon_admin.common.error.exception import BadRequestException, NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterResponseDto, CenterUpdateRequestDto, CenterOperatingTimeDto, \
    CenterHoldInfoDto, CenterWallDto, CenterHoldDto, CenterCoreUpdateRequestDto
from claon_admin.schema.center import Center, CenterHold, CenterWall
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for update center")
class TestUpdate(object):
    @pytest.fixture
    async def center_update_request_dto(self):
        yield CenterUpdateRequestDto(
            center=CenterCoreUpdateRequestDto(
                profile_image="https://test.profile.png",
                address="서울시 강남구",
                detail_address="상세 주소",
                tel="010-1234-5678",
                web_url="http://test.com",
                instagram_name="test_instagram",
                youtube_code="@test",
                image_list=["https://test.image.png"],
                utility_list=["test_utility"],
                operating_time_list=[CenterOperatingTimeDto(day_of_week="월", start_time="09:00", end_time="18:00")],
            ),
            hold_info=CenterHoldInfoDto(is_color=False, hold_list=[CenterHoldDto(name="hold", difficulty="hard")]),
            wall_list=[CenterWallDto(name="wall", wall_type=WallType.ENDURANCE)],
        )

    @pytest.mark.asyncio
    @pytest.mark.it('Success case')
    async def test_update(
            self,
            mock_repo: dict,
            center_service: CenterService,
            center_fixture: Center,
            center_holds_fixture: List[CenterHold],
            center_walls_fixture: List[CenterWall],
            center_update_request_dto: CenterUpdateRequestDto
    ):
        # given
        center_fixture.holds = center_holds_fixture
        center_fixture.walls = center_walls_fixture
        center_fixture.update(**center_update_request_dto.center.dict())

        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.ADMIN)

        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]
        mock_repo["center_hold"].save_all.side_effect = [center_holds_fixture]
        mock_repo["center_wall"].save_all.side_effect = [center_walls_fixture]

        response = CenterResponseDto.from_entity(entity=center_fixture,
                                                 holds=center_holds_fixture,
                                                 walls=center_walls_fixture)

        # when
        result = await center_service.update(center_id=center_fixture.id, subject=request_user,
                                             dto=center_update_request_dto)
        # then
        assert result == response

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: center is not found')
    async def test_update_with_not_exist_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            center_update_request_dto: CenterUpdateRequestDto
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [None]

        # when
        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.update(center_id="wrong id", subject=request_user, dto=center_update_request_dto)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: center is already deleted')
    async def test_update_with_none_user_id(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            center_update_request_dto: CenterUpdateRequestDto
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
        center_fixture.user_id = None
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]

        with pytest.raises(BadRequestException) as exception:
            # when
            await center_service.update(center_id=center_fixture.id, subject=request_user,
                                        dto=center_update_request_dto)

        # then
        assert exception.value.code == ErrorCode.ROW_ALREADY_DETELED

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: request user is not admin')
    async def test_update_with_not_center_admin(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            center_update_request_dto: CenterUpdateRequestDto
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id_with_details.side_effect = [center_fixture]

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.update(center_id=center_fixture.id, subject=request_user,
                                        dto=center_update_request_dto)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
