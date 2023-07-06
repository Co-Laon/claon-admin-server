from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from claon_admin.common.util.auth import CurrentUser
from claon_admin.container import Container
from claon_admin.model.membership import MembershipIssueResponseDto, MembershipIssueRequestDto, MembershipResponseDto, \
    MembershipCountUpdateRequestDto, MembershipExpireRequestDto
from claon_admin.service.membership import MembershipService

router = APIRouter()


@cbv(router)
class MembershipRouter:
    @inject
    def __init__(self,
                 membership_service: MembershipService = Depends(Provide[Container.membership_service])):
        self.membership_service = membership_service

    @router.put('/subtract', response_model=List[MembershipResponseDto])
    async def update_membership_count(self,
                                      subject: CurrentUser,
                                      request_dto: MembershipCountUpdateRequestDto):
        pass

    @router.put('/expire', response_model=List[MembershipResponseDto])
    async def expire_membership(self,
                                subject: CurrentUser,
                                request_dto: MembershipExpireRequestDto):
        pass

    @router.post('/issue', response_model=MembershipIssueResponseDto)
    async def issue_membership(self,
                               subject: CurrentUser,
                               request_dto: MembershipIssueRequestDto):
        pass
