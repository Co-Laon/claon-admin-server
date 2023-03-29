from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.container import db
from claon_admin.model.center import CenterNameResponseDto, CenterResponseDto, UploadFileResponseDto
from claon_admin.model.enum import CenterUploadPurpose

router = APIRouter()


@cbv(router)
class CenterRouter:
    def __init__(self):
        pass

    @router.get('/name/{name}', response_model=CenterNameResponseDto)
    async def get_name(self,
                       name: str,
                       session: AsyncSession = Depends(db.get_db)):
        pass

    @router.get('/{center_id}', response_model=CenterResponseDto)
    async def find_by_id(self,
                         center_id: str,
                         session: AsyncSession = Depends(db.get_db)):
        pass

    @router.post('/{purpose}/file', response_model=UploadFileResponseDto)
    async def upload(self,
                     purpose: CenterUploadPurpose,
                     file: UploadFile = File(...)):
        pass
