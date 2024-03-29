from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from claon_admin.common.error.exception import UnauthorizedException, ErrorCode
from claon_admin.common.util.db import db
from claon_admin.common.util.jwt import resolve_access_token
from claon_admin.common.util.redis import find_user_id_by_refresh_key, delete_refresh_key, save_refresh_key
from claon_admin.container import Container
from claon_admin.model.auth import RequestUser
from claon_admin.schema.user import UserRepository


@inject
async def __find_user_by_id(
        user_id: str,
        user_repository: UserRepository = Depends(Provide[Container.user_repository])
):
    async with db.async_session_maker() as session:
        user = await user_repository.find_by_id(session, user_id)
        if user is None:
            raise UnauthorizedException(
                ErrorCode.USER_DOES_NOT_EXIST,
                "Not existing user account."
            )
        return user


async def get_subject(
    token: HTTPAuthorizationCredentials
) -> RequestUser:
    token = token.dict().get("credentials")
    payload = resolve_access_token(token)

    user = await __find_user_by_id(user_id=payload.get("sub"))

    return RequestUser(
        id=user.id,
        profile_img=user.profile_img,
        nickname=user.nickname,
        sns=user.sns,
        email=user.email,
        instagram_nickname=user.instagram_name,
        role=user.role
    )


async def get_refresh(
    refresh_key: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> RequestUser:
    refresh_key = refresh_key.dict().get("credentials")

    user_id = find_user_id_by_refresh_key(refresh_key)

    if user_id is None:
        raise UnauthorizedException(
            ErrorCode.EXPIRED_JWT,
            "refresh key is expired."
        )

    user = await __find_user_by_id(user_id=user_id)

    delete_refresh_key(refresh_key=refresh_key)
    save_refresh_key(refresh_key=refresh_key, user_id=user_id)

    return RequestUser(
        id=user.id,
        profile_img=user.profile_img,
        nickname=user.nickname,
        email=user.email,
        sns=user.sns,
        instagram_nickname=user.instagram_name,
        role=user.role
    )


async def get_user(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    return await get_subject(token)


async def get_center_admin(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    user = await get_subject(token)

    if not user.is_center_admin():
        raise UnauthorizedException(
            ErrorCode.NOT_ACCESSIBLE,
            "암장 관리자가 아닙니다."
        )

    return user


async def get_admin(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer())
):
    user = await get_subject(token)

    if not user.is_admin():
        raise UnauthorizedException(
            ErrorCode.NONE_ADMIN_ACCOUNT,
            "어드민 권한이 없습니다."
        )

    return user


CurrentUser = Annotated[RequestUser, Depends(get_user)]
AdminUser = Annotated[RequestUser, Depends(get_admin)]
CenterAdminUser = Annotated[RequestUser, Depends(get_center_admin)]
CurrentRefreshUser = Annotated[RequestUser, Depends(get_refresh)]
