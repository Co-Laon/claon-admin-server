from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.config.auth import get_subject
from claon_admin.container import Container, db
from claon_admin.model.auth import RequestUser
from claon_admin.model.center import CenterRequestDto, CenterResponseDto
from claon_admin.model.enum import OAuthProvider
from claon_admin.model.user import SignInRequestDto, LectorRequestDto, JwtResponseDto, UserProfileResponseDto, \
    IsDuplicatedNicknameResponseDto, LectorResponseDto
from claon_admin.service.user import UserService

router = APIRouter()


@cbv(router)
class AuthRouter:
    @inject
    def __init__(self,
                 user_service: UserService = Depends(Provide[Container.user_service])):
        self.user_service = user_service

    @router.post('/{provider}/sign-in', response_model=JwtResponseDto)
    async def sign_in(self,
                      provider: OAuthProvider,
                      dto: SignInRequestDto,
                      session: AsyncSession = Depends(db.get_db)):
        pass

    @router.post('/center/sign-up', response_model=CenterResponseDto)
    async def center_sign_up(self,
                             dto: CenterRequestDto,
                             session: AsyncSession = Depends(db.get_db),
                             subject: RequestUser = Depends(get_subject)):
        return await self.user_service.sign_up_center(session, dto)

    @router.post('/lector/sign-up', response_model=LectorResponseDto)
    async def lector_sign_up(self,
                             dto: LectorRequestDto,
                             session: AsyncSession = Depends(db.get_db),
                             subject: RequestUser = Depends(get_subject)):
        return await self.user_service.sign_up_lector(session, dto)

    @router.get('/nickname/{nickname}/is-duplicated', response_model=IsDuplicatedNicknameResponseDto)
    async def is_duplicated_nickname(self,
                                     nickname: str,
                                     session: AsyncSession = Depends(db.get_db)):
        return await self.user_service.check_nickname_duplication(session, nickname)
