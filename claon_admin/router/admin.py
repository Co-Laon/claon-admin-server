from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.config.auth import get_subject
from claon_admin.container import db, Container
from claon_admin.model.admin import LectorResponseDto, CenterResponseDto
from claon_admin.model.auth import RequestUser
from claon_admin.service.user import UserService

router = APIRouter()


@cbv(router)
class AdminRouter:
    @inject
    def __init__(self,
                 user_service: UserService = Depends(Provide[Container.user_service])):
        self.user_service = user_service

    @router.get('/lectors/approve', response_model=List[LectorResponseDto])
    async def find_approval_pending_lectors(self,
                                            session: AsyncSession = Depends(db.get_db)):
        pass

    @router.post('/lectors/{lector_id}/approve')
    async def approve_lector(self,
                             lector_id: str,
                             session: AsyncSession = Depends(db.get_db),
                             subject: RequestUser = Depends(get_subject)):
        return await self.user_service.approve_lector(lector_id, session, subject)

    @router.delete('/lectors/{lector_id}/reject')
    async def reject_lector(self,
                            lector_id: str,
                            session: AsyncSession = Depends(db.get_db),
                            subject: RequestUser = Depends(get_subject)):
        return await self.user_service.reject_lector(lector_id, session, subject)

    @router.get('/center/approve', response_model=List[CenterResponseDto])
    async def find_approval_pending_centers(self,
                                            session: AsyncSession = Depends(db.get_db)):
        pass

    @router.post('/center/{center_id}/approve')
    async def approve_center(self,
                             center_id: str,
                             session: AsyncSession = Depends(db.get_db),
                             subject: RequestUser = Depends(get_subject)):
        return await self.user_service.approve_center(center_id, session, subject)

    @router.delete('/center/{center_id}/reject')
    async def reject_center(self,
                            center_id: str,
                            session: AsyncSession = Depends(db.get_db),
                            subject: RequestUser = Depends(get_subject)):
        return await self.user_service.reject_center(center_id, session, subject)
