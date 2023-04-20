from typing import List

from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.container import db
from claon_admin.model.user import CenterNameResponseDto

router = APIRouter()


@cbv(router)
class UserRouter:
    def __init__(self):
        pass

    @router.get('/centers', response_model=List[CenterNameResponseDto])
    async def find_center(self,
                          session: AsyncSession = Depends(db.get_db)):
        pass
