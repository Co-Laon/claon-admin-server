from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from claon_admin.common.enum import MemberInfoSearchOrder, MemberInfoSearchStatus, MembershipIssuanceInfoSearchOrder, \
    MembershipIssuanceInfoSearchStatus
from claon_admin.common.util.auth import CurrentUser
from claon_admin.common.util.pagination import Pagination
from claon_admin.container import Container
from claon_admin.model.membership import MemberSummaryResponseDto, MemberBriefResponseDto, MemberDetailResponseDto, \
    MembershipIssueResponseDto, MembershipIssueRequestDto, IssuedMembershipSummaryResponseDto, \
    IssuedMembershipBriefResponseDto, IssuedMembershipResponseDto
from claon_admin.service.membership import MembershipService

router = APIRouter()


@cbv(router)
class MembershipRouter:
    @inject
    def __init__(self,
                 membership_service: MembershipService = Depends(Provide[Container.membership_service])):
        self.membership_service = membership_service

    @router.put('/{membership_id}', response_model=IssuedMembershipResponseDto)
    async def update_issued_membership_count(self,
                                             subject: CurrentUser,
                                             membership_id: str):
        pass

    @router.post('/issue', response_model=MembershipIssueResponseDto)
    async def issue_membership(self,
                               subject: CurrentUser,
                               request_dto: MembershipIssueRequestDto):
        pass

    @router.get('/members/summary', response_model=MemberSummaryResponseDto)
    async def find_members_summary_by_center(self,
                                             subject: CurrentUser,
                                             center_id: str):
        pass

    @router.get('/members/{nickname}', response_model=Pagination[MemberBriefResponseDto])
    async def find_member_by_name(self,
                                  subject: CurrentUser,
                                  center_id: str,
                                  nickname: str,
                                  order: MemberInfoSearchOrder | None = None,
                                  member_status: MemberInfoSearchStatus | None = None):
        pass

    @router.get('/members/{member_id}', response_model=MemberDetailResponseDto)
    async def find_member_detail_by_id(self,
                                       subject: CurrentUser,
                                       center_id: str,
                                       member_id: str):
        pass

    @router.get('/summary', response_model=IssuedMembershipSummaryResponseDto)
    async def find_issued_memberships_summary_by_center(self,
                                                        subject: CurrentUser):
        pass

    @router.get('/', response_model=Pagination[IssuedMembershipBriefResponseDto])
    async def find_issued_memberships_by_center(self,
                                                subject: CurrentUser,
                                                center_id: str):
        pass

    @router.get('/members/{nickname}', response_model=Pagination[IssuedMembershipBriefResponseDto])
    async def find_issued_membership_by_nickname(self,
                                                 subject: CurrentUser,
                                                 nickname: str,
                                                 order: MembershipIssuanceInfoSearchOrder | None = None,
                                                 membership_status: MembershipIssuanceInfoSearchStatus | None = None):
        pass
