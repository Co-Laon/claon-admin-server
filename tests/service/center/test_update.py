# from typing import List

# import pytest

# from claon_admin.common.enum import Role
# from claon_admin.common.error.exception import BadRequestException, NotFoundException, ErrorCode, UnauthorizedException
# from claon_admin.model.auth import RequestUser
# from claon_admin.model.center import CenterResponseDto, CenterUpdateRequestDto
# from claon_admin.schema.center import Center, CenterFee, CenterHold, CenterWall
# from claon_admin.service.center import CenterService

# @pytest.mark.describe("Test case for update center")
# class TestUpdate(object):
#     @pytest.mark.asyncio
#     @pytest.mark.it('Success case')
#     async def test_update(
#             self,
#             center_service: CenterService,
#             mock_repo: dict,
#             center_fixture: Center,
#             another_center_fixture: Center,
#             center_fees_fixture: List[CenterFee],
#             center_holds_fixture: List[CenterHold],
#             center_walls_fixture: List[CenterWall],
#             another_center_fees_fixture: List[CenterFee],
#             another_center_holds_fixture: List[CenterHold],
#             another_center_walls_fixture: List[CenterWall]
#     ):
#         # given
#         another_center_fixture.id = center_fixture.id
#         another_center_fixture.fees = another_center_fees_fixture
#         another_center_fixture.holds = another_center_holds_fixture
#         another_center_fixture.walls = another_center_walls_fixture
        
#         request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.ADMIN)
#         request = CenterUpdateRequestDto.from_entity(entity=another_center_fixture, 
#                                                      fees=another_center_fees_fixture, 
#                                                      holds=another_center_holds_fixture, 
#                                                      walls=another_center_walls_fixture)

#         mock_repo["center"].find_by_id.side_effect = [center_fixture]

#         mock_repo["center_fee"].save_all.side_effect = [another_center_fees_fixture]
#         mock_repo["center_hold"].save_all.side_effect = [another_center_holds_fixture]
#         mock_repo["center_wall"].save_all.side_effect = [another_center_walls_fixture]
#         mock_repo["center"].update.side_effect = [another_center_fixture]

#         response = CenterResponseDto.from_entity(entity=another_center_fixture,
#                                                  holds=another_center_holds_fixture,
#                                                  walls=another_center_walls_fixture,
#                                                  fees=another_center_fees_fixture)
        
#         # when
#         result = await center_service.update(center_id=center_fixture.id, subject=request_user, dto=request)

#         # then
#         assert result == response

#     @pytest.mark.asyncio
#     @pytest.mark.it('Fail case: center is not found')
#     async def test_update_with_not_exist_center(
#             self,
#             center_service: CenterService,
#             mock_repo: dict,
#             center_fixture: Center,
#             center_fees_fixture: List[CenterFee],
#             center_holds_fixture: List[CenterHold],
#             center_walls_fixture: List[CenterWall]
#     ):
#         # given
#         request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.ADMIN)
#         request = CenterUpdateRequestDto.from_entity(center_fixture, center_fees_fixture, center_holds_fixture, center_walls_fixture)
#         mock_repo["center"].find_by_id.side_effect = [None]
        
#         # when
#         with pytest.raises(NotFoundException) as exception:
#             # when
#             await center_service.update(center_id="wrong id", subject=request_user, dto=request)

#         # then
#         assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

#     @pytest.mark.asyncio
#     @pytest.mark.it('Fail case: center is already deleted')
#     async def test_update_with_none_user_id(
#             self,
#             center_service: CenterService,
#             mock_repo: dict,
#             center_fixture: Center,
#             center_fees_fixture: List[CenterFee],
#             center_holds_fixture: List[CenterHold],
#             center_walls_fixture: List[CenterWall]
#     ):
#         # given
#         request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.ADMIN)
#         request = CenterUpdateRequestDto.from_entity(center_fixture, center_fees_fixture, center_holds_fixture, center_walls_fixture)
        
#         deleted_center = center_fixture
#         deleted_center.user_id = None
#         mock_repo["center"].find_by_id.side_effect = [deleted_center]
        
#         with pytest.raises(BadRequestException) as exception:
#             # when
#             await center_service.update(center_id=center_fixture.id, subject=request_user, dto=request)

#         # then
#         assert exception.value.code == ErrorCode.ROW_ALREADY_DETELED

#     @pytest.mark.asyncio
#     @pytest.mark.it('Fail case: request user is not admin')
#     async def test_update_with_not_center_admin(
#             self,
#             center_service: CenterService,
#             mock_repo: dict,
#             center_fixture: Center,
#             center_fees_fixture: List[CenterFee],
#             center_holds_fixture: List[CenterHold],
#             center_walls_fixture: List[CenterWall]
#     ):
#         # given
#         request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
#         request = CenterUpdateRequestDto.from_entity(center_fixture, center_fees_fixture, center_holds_fixture, center_walls_fixture)
        
#         mock_repo["center"].find_by_id.side_effect = [center_fixture]
        
#         with pytest.raises(UnauthorizedException) as exception:
#             # when
#             await center_service.update(center_id=center_fixture.id, subject=request_user, dto=request)

#         # then
#         assert exception.value.code == ErrorCode.NOT_ACCESSIBLE

