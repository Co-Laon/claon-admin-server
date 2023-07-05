from typing import List

import pytest

from claon_admin.common.enum import Role, WallType
from claon_admin.common.error.exception import BadRequestException, ErrorCode
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterAuthRequestDto, CenterOperatingTimeDto, CenterHoldInfoDto, CenterWallDto, \
    CenterHoldDto, CenterCoreCreateRequestDto
from claon_admin.model.user import UserProfileDto
from claon_admin.schema.center import Center, CenterHold, CenterWall, CenterApprovedFile
from claon_admin.schema.user import User
from claon_admin.service.user import UserService


@pytest.mark.describe("Test case for sign up center")
class TestSignUpCenter(object):
    @pytest.fixture
    async def center_request_dto(self, user_fixture: User):
        yield CenterAuthRequestDto(
            profile=UserProfileDto(
                profile_image=user_fixture.profile_img,
                nickname=user_fixture.nickname,
                email=user_fixture.email,
                instagram_nickname=user_fixture.instagram_name
            ),
            center=CenterCoreCreateRequestDto(
                profile_image="https://test.profile.png",
                name="test center",
                address="test_address",
                detail_address="test_detail_address",
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
            proof_list=["https://example.com/approved.jpg"]
        )

    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_sign_up_center(
            self,
            mock_repo: dict,
            user_service: UserService,
            user_fixture: User,
            center_fixture: Center,
            center_holds_fixture: List[CenterHold],
            center_walls_fixture: List[CenterWall],
            center_approved_files_fixture: List[CenterApprovedFile],
            center_request_dto: CenterAuthRequestDto
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
        mock_repo["user"].exist_by_nickname.side_effect = [False]
        mock_repo["user"].find_by_id.side_effect = [user_fixture]
        mock_repo["center"].save.side_effect = [center_fixture]
        mock_repo["center_hold"].save_all.side_effect = [center_holds_fixture]
        mock_repo["center_wall"].save_all.side_effect = [center_walls_fixture]
        mock_repo["center_approved_file"].save_all.side_effect = [center_approved_files_fixture]

        # when
        result = await user_service.sign_up_center(request_user, center_request_dto)

        # then
        assert result.profile_image == center_request_dto.center.profile_image
        assert result.name == center_request_dto.center.name
        assert result.address == center_request_dto.center.address
        assert result.detail_address == center_request_dto.center.detail_address
        assert result.tel == center_request_dto.center.tel
        assert result.web_url == center_request_dto.center.web_url
        assert result.instagram_name == center_request_dto.center.instagram_name
        assert result.youtube_code == center_request_dto.center.youtube_code
        assert result.image_list == center_request_dto.center.image_list
        assert result.utility_list == center_request_dto.center.utility_list
        assert result.operating_time_list == center_request_dto.center.operating_time_list
        assert result.hold_info == center_request_dto.hold_info
        assert result.wall_list == center_request_dto.wall_list

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: user nickname already exist")
    async def test_sign_up_center_existing_nickname(
            self,
            mock_repo: dict,
            user_service: UserService,
            center_request_dto: CenterAuthRequestDto
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.PENDING)
        mock_repo["user"].exist_by_nickname.side_effect = [True]

        with pytest.raises(BadRequestException) as exception:
            # when
            await user_service.sign_up_center(request_user, center_request_dto)

        # then
        assert exception.value.code == ErrorCode.DUPLICATED_NICKNAME

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: user already sign up")
    async def test_sign_up_center_already_sign_up(
            self,
            mock_repo: dict,
            user_service: UserService,
            center_request_dto: CenterAuthRequestDto
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)

        with pytest.raises(BadRequestException) as exception:
            # when
            await user_service.sign_up_center(request_user, center_request_dto)

        # then
        assert exception.value.code == ErrorCode.USER_ALREADY_SIGNED_UP
