from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from claon_admin.common.error.exception import UnauthorizedException, ErrorCode
from claon_admin.common.util.db import db
from claon_admin.common.util.jwt import resolve_token, resolve_refresh_token
from claon_admin.common.util.redis import find_user_id_by_refresh_token
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
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> RequestUser:
    token = token.dict().get("credentials")
    payload = resolve_token(token)

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
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> RequestUser:
    token = token.dict().get("credentials")
    resolve_refresh_token(token)

    user_id = find_user_id_by_refresh_token(token)

    if user_id is None:
        raise UnauthorizedException(
            ErrorCode.EXPIRED_JWT,
            "token is expired."
        )

    user = await __find_user_by_id(user_id=user_id)

    return RequestUser(
        id=user.id,
        profile_img=user.profile_img,
        nickname=user.nickname,
        email=user.email,
        sns=user.sns,
        instagram_nickname=user.instagram_name,
        role=user.role
    )

CurrentUser = Annotated[RequestUser, Depends(get_subject)]
CurrentRefreshUser = Annotated[RequestUser, Depends(get_refresh)]
