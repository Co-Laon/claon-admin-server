from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from claon_admin.common.enum import OAuthProvider
from claon_admin.common.util.auth import CurrentUser, CurrentRefreshUser
from claon_admin.container import Container
from claon_admin.model.center import CenterAuthRequestDto, CenterResponseDto
from claon_admin.model.user import SignInRequestDto, LectorRequestDto, JwtResponseDto, \
    IsDuplicatedNicknameResponseDto, LectorResponseDto, JwtReissueDto
from claon_admin.service.user import UserService

router = APIRouter()


@cbv(router)
class AuthRouter:
    @inject
    def __init__(self,
                 user_service: UserService = Depends(Provide[Container.user_service])):
        self.user_service = user_service

    # TODO: Need to be removed later
    @router.post('/test-sign-in', response_model=JwtResponseDto)
    async def test_sign_in(self,
                           dto: SignInRequestDto):
        return await self.user_service.test_sign_in(dto)

    @router.post('/{provider}/sign-in', response_model=JwtResponseDto)
    async def sign_in(self,
                      provider: OAuthProvider,
                      dto: SignInRequestDto):
        return await self.user_service.sign_in(provider, dto)

    @router.get('/reissue', response_model=JwtReissueDto)
    async def reissue_token(self,
                            subject: CurrentRefreshUser):
        return await self.user_service.reissue_token(subject)

    @router.post('/center/sign-up', response_model=CenterResponseDto)
    async def center_sign_up(self,
                             subject: CurrentUser,
                             dto: CenterAuthRequestDto):
        return await self.user_service.sign_up_center(subject, dto)

    @router.post('/lector/sign-up', response_model=LectorResponseDto)
    async def lector_sign_up(self,
                             subject: CurrentUser,
                             dto: LectorRequestDto):
        return await self.user_service.sign_up_lector(subject, dto)

    @router.get('/nickname/{nickname}/is-duplicated', response_model=IsDuplicatedNicknameResponseDto)
    async def is_duplicated_nickname(self,
                                     nickname: str):
        return await self.user_service.check_nickname_duplication(nickname)
