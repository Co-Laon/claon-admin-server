import pytest

from claon_admin.common.enum import WallType, Role
from claon_admin.common.error.exception import UnauthorizedException, ErrorCode
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterRequestDto, CenterOperatingTimeDto, CenterFeeDto, CenterHoldInfoDto, \
    CenterHoldDto, CenterWallDto, CenterResponseDto
from claon_admin.schema.center import Center, CenterFee, CenterWall, CenterHold, CenterApprovedFile
from claon_admin.schema.user import User
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for save center")
class TestSave(object):
    @pytest.fixture
    async def center_save_request_dto(self):
        yield CenterRequestDto(
            profile_image="test_profile_image",
            name="test name",
            address="test_address",
            detail_address="test_detail_address",
            tel="010-1111-1111",
            web_url="test_web_url",
            instagram_name="test_instagram_name",
            youtube_code="@testsave",
            image_list=["test_image"],
            utility_list=["test_utility"],
            operating_time_list=[CenterOperatingTimeDto(day_of_week="월", start_time="10:00", end_time="15:00")],
            fee_list=[CenterFeeDto(name="fee_name", price=1000, count=10)],
            hold_info=CenterHoldInfoDto(is_color=True, hold_list=[CenterHoldDto(difficulty="red", name="name")]),
            wall_list=[CenterWallDto(wall_type=WallType.BOULDERING, name="wall")],
            proof_list=["test_proof"]
        )

    @pytest.mark.asyncio
    @pytest.mark.it("Success cases for saving center")
    async def test_save(
            self,
            mock_repo: dict,
            center_service: CenterService,
            user_fixture: User,
            new_center_fixture: Center,
            new_center_holds_fixture: CenterHold,
            new_center_walls_fixture: CenterWall,
            new_approved_file_fixture: CenterApprovedFile,
            center_save_request_dto: CenterRequestDto
    ):
        # given
        request_user = RequestUser(id=user_fixture.id, sns="test@claon.com", role=Role.CENTER_ADMIN)

        mock_repo["center"].save.side_effect = [new_center_fixture]
        mock_repo["center_hold"].save_all.side_effect = [new_center_holds_fixture]
        mock_repo["center_wall"].save_all.side_effect = [new_center_walls_fixture]
        mock_repo["center_approved_file"].save_all.side_effect = [new_approved_file_fixture]

        response = CenterResponseDto.from_entity(
            entity=new_center_fixture,
            holds=new_center_holds_fixture,
            walls=new_center_walls_fixture
        )

        # when
        result = await center_service.create(subject=request_user, dto=center_save_request_dto)

        # then
        assert result == response

    @pytest.mark.asyncio
    @pytest.mark.it('Fail case: request user is not center admin')
    async def test_save_with_not_center_admin(
            self,
            center_service: CenterService,
            center_save_request_dto: CenterRequestDto
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.USER)

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.create(subject=request_user, dto=center_save_request_dto)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
