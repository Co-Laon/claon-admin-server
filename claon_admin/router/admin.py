from typing import List

from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.container import db
from claon_admin.model.admin import LectorResponseDto, CenterResponseDto

router = APIRouter()


@cbv(router)
class AdminRouter:
    def __init__(self):
        pass

    @router.get('/lectors/approve', response_model=List[LectorResponseDto])
    async def find_approval_pending_lectors(self,
                                            session: AsyncSession = Depends(db.get_db)):
        pass

    @router.post('/lectors/{lector_id}/approve')
    async def approve_lector(self,
                             lector_id: str,
                             session: AsyncSession = Depends(db.get_db)):
        pass

    @router.delete('/lectors/{lector_id}/reject')
    async def reject_lector(self,
                            lector_id: str,
                            session: AsyncSession = Depends(db.get_db)):
        pass

    @router.get('/center/approve', response_model=List[CenterResponseDto])
    async def find_approval_pending_centers(self,
                                            session: AsyncSession = Depends(db.get_db)):
        pass

    @router.post('/center/{center_id}/approve')
    async def approve_center(self,
                             center_id: str,
                             session: AsyncSession = Depends(db.get_db)):
        pass

    @router.delete('/center/{center_id}/reject')
    async def reject_center(self,
                            center_id: str,
                            session: AsyncSession = Depends(db.get_db)):
        pass
