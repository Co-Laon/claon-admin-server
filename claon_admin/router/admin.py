from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from claon_admin.common.annotated import Session, CurrentUser
from claon_admin.container import Container
from claon_admin.model.admin import LectorResponseDto, CenterResponseDto
from claon_admin.service.admin import AdminService

router = APIRouter()


@cbv(router)
class AdminRouter:
    @inject
    def __init__(self,
                 admin_service: AdminService = Depends(Provide[Container.admin_service])):
        self.admin_service = admin_service

    @router.get("/lectors/approve", response_model=List[LectorResponseDto])
    async def find_approval_pending_lectors(self,
                                            session: Session,
                                            subject: CurrentUser):
        return await self.admin_service.get_unapproved_lectors(session, subject)

    @router.post('/lectors/{lector_id}/approve')
    async def approve_lector(self,
                             session: Session,
                             subject: CurrentUser,
                             lector_id: str):
        return await self.admin_service.approve_lector(session, subject, lector_id)

    @router.delete('/lectors/{lector_id}/reject')
    async def reject_lector(self,
                            session: Session,
                            subject: CurrentUser,
                            lector_id: str):
        return await self.admin_service.reject_lector(session, subject, lector_id)

    @router.get('/centers/approve', response_model=List[CenterResponseDto])
    async def find_approval_pending_centers(self,
                                            session: Session,
                                            subject: CurrentUser):
        return await self.admin_service.get_unapproved_centers(session, subject)

    @router.post('/centers/{center_id}/approve')
    async def approve_center(self,
                             session: Session,
                             subject: CurrentUser,
                             center_id: str):
        return await self.admin_service.approve_center(session, subject, center_id)

    @router.delete('/centers/{center_id}/reject')
    async def reject_center(self,
                            session: Session,
                            subject: CurrentUser,
                            center_id: str):
        return await self.admin_service.reject_center(session, subject, center_id)
