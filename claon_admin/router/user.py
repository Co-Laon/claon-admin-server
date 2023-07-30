from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_pagination import Params
from fastapi_utils.cbv import cbv

from claon_admin.common.enum import LectorUploadPurpose
from claon_admin.common.util.auth import CurrentUser
from claon_admin.common.util.pagination import Pagination
from claon_admin.container import Container
from claon_admin.model.auth import RequestUser
from claon_admin.model.file import UploadFileResponseDto
from claon_admin.model.user import CenterNameResponseDto, UserNameResponseDto
from claon_admin.service.user import UserService

router = APIRouter()


@cbv(router)
class UserRouter:
    @inject
    def __init__(self,
                 user_service: UserService = Depends(Provide[Container.user_service])):
        self.user_service = user_service

    @router.get('/centers', response_model=List[CenterNameResponseDto])
    async def find_center(self,
                          subject: CurrentUser):
        return await self.user_service.find_centers(subject)

    # s3 upload
    @router.post('/profile', response_model=UploadFileResponseDto)
    async def upload_profile(self,
                             subject: CurrentUser,
                             file: UploadFile = File(...)):
        return await self.user_service.upload_profile(file)

    @router.post('/{purpose}/file', response_model=UploadFileResponseDto)
    async def upload(self,
                     subject: RequestUser,
                     purpose: LectorUploadPurpose,
                     file: UploadFile = File(...)):
        return await self.user_service.upload_file(purpose, file)

    @router.get('/nickname/{nickname}', response_model=Pagination[UserNameResponseDto])
    async def find_all_by_nickname(self,
                                   nickname: str,
                                   params: Params = Depends()):
        return await self.user_service.find_all_by_nickname(params, nickname)
