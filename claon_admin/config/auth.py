from dependency_injector.wiring import Provide, inject
from fastapi import Header, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import UnauthorizedException, ErrorCode, InternalServerException
from claon_admin.common.util.db import db
from claon_admin.common.util.header import add_jwt_tokens
from claon_admin.common.util.jwt import resolve_access_token, resolve_refresh_token, is_expired, create_access_token, \
    reissue_refresh_token
from claon_admin.common.util.redis import find_user_id_by_refresh_token
from claon_admin.container import Container
from claon_admin.model.auth import RequestUser
from claon_admin.schema.user import UserRepository


@inject
async def get_subject(
    response: Response,
    access_token: str = Header(None),
    refresh_token: str = Header(None),
    session: AsyncSession = Depends(db.get_db),
    user_repository: UserRepository = Depends(Provide[Container.user_repository])
) -> RequestUser:
    try:
        if access_token is None:
            raise UnauthorizedException(
                ErrorCode.NOT_SIGN_IN,
                "Cannot find access token from request header."
            )

        if refresh_token is None:
            raise UnauthorizedException(
                ErrorCode.NOT_SIGN_IN,
                "Cannot find refresh token from request header."
            )

        access_payload = resolve_access_token(access_token)
        refresh_payload = resolve_refresh_token(refresh_token)

        if is_expired(access_payload):
            if is_expired(refresh_payload):
                raise UnauthorizedException(
                    ErrorCode.INVALID_JWT,
                    "Both access token and refresh token are expired."
                )

            user_id = find_user_id_by_refresh_token(refresh_token)
            if user_id is None:
                raise UnauthorizedException(
                    ErrorCode.INVALID_JWT,
                    "Refresh token is not valid."
                )

            add_jwt_tokens(
                response,
                create_access_token(user_id),
                reissue_refresh_token(refresh_token, user_id),
            )

            user = await user_repository.find_by_id(session, user_id)
            if user is None:
                raise UnauthorizedException(
                    ErrorCode.USER_DOES_NOT_EXIST,
                    "Not existing user account."
                )

            return RequestUser(
                id=user.id,
                profile_img=user.profile_img,
                nickname=user.nickname,
                email=user.email,
                instagram_nickname=user.instagram_name,
                role=user.role
            )
        else:
            if is_expired(refresh_payload):
                raise UnauthorizedException(
                    ErrorCode.INVALID_JWT,
                    "Refresh token is expired."
                )

            user = await user_repository.find_by_id(session, access_payload.get("sub"))
            if user is None:
                raise UnauthorizedException(
                    ErrorCode.USER_DOES_NOT_EXIST,
                    "Not existing user account."
                )

            return RequestUser(
                id=user.id,
                profile_img=user.profile_img,
                nickname=user.nickname,
                email=user.email,
                instagram_nickname=user.instagram_name,
                role=user.role
            )
    except Exception as e:
        raise InternalServerException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            "Unexpected error occurred when getting and parsing tokens."
        ) from e
