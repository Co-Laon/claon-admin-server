from datetime import datetime, timedelta

from fastapi import Header, Depends, Response
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import UnauthorizedException, InternalServerException
from claon_admin.common.error.exception import ErrorCode
from claon_admin.common.util.header import add_jwt_tokens
from claon_admin.common.util.redis import save_refresh_token, find_user_id_by_refresh_token, delete_refresh_token
from claon_admin.config.consts import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY, \
    REFRESH_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_SECRET_KEY, TIME_ZONE_KST
from claon_admin.container import db
from claon_admin.model.user import UserProfileDto
from claon_admin.schema.user import UserRepository


def create_access_token(user_id: str) -> str:
    to_encode = {
        "sub": user_id,
        "exp": datetime.now(TIME_ZONE_KST) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    return jwt.encode(to_encode, JWT_SECRET_KEY, JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    to_encode = {
        "exp": datetime.now(TIME_ZONE_KST) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    }

    token = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, JWT_ALGORITHM)
    save_refresh_token(token, user_id)
    return token


def reissue_refresh_token(refresh_token: str, user_id: str) -> str:
    delete_refresh_token(refresh_token)
    return create_refresh_token(user_id)


def resolve_access_token(access_token: str) -> dict:
    try:
        return jwt.decode(
            access_token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": False}
        )
    except jwt.JWTError:
        raise UnauthorizedException(
            ErrorCode.INVALID_JWT,
            "Invalid access token."
        )


def resolve_refresh_token(refresh_token: str) -> dict:
    try:
        return jwt.decode(
            refresh_token,
            JWT_REFRESH_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": False}
        )
    except jwt.JWTError:
        raise UnauthorizedException(
            ErrorCode.INVALID_JWT,
            "Invalid refresh token."
        )


def is_expired(payload: dict):
    if datetime.now(TIME_ZONE_KST) > datetime.fromtimestamp(payload.get("exp"), TIME_ZONE_KST):
        return True
    return False


async def get_subject(
        response: Response,
        access_token: str = Header(None),
        refresh_token: str = Header(None),
        session: AsyncSession = Depends(db.get_db)
) -> UserProfileDto:
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

            add_jwt_tokens(response, create_access_token(user_id), reissue_refresh_token(refresh_token, user_id))

            user = await UserRepository.find_by_id(session, user_id)
            if user is None:
                raise UnauthorizedException(
                    ErrorCode.USER_DOES_NOT_EXIST,
                    "Not existing user account."
                )

            return UserProfileDto(
                profile_image=user.profile_image,
                nickname=user.nickname,
                email=user.email,
                instagram_nickname=user.instagram_nickname,
                role=user.role
            )
        else:
            if is_expired(refresh_payload):
                raise UnauthorizedException(
                    ErrorCode.INVALID_JWT,
                    "Refresh token is expired."
                )

            user = await UserRepository.find_by_id(session, access_payload.get("sub"))
            if user is None:
                raise UnauthorizedException(
                    ErrorCode.USER_DOES_NOT_EXIST,
                    "Not existing user account."
                )

            return UserProfileDto(
                profile_image=user.profile_image,
                nickname=user.nickname,
                email=user.email,
                instagram_nickname=user.instagram_nickname,
                role=user.role
            )
    except Exception:
        raise InternalServerException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            "Unexpected error occurred when getting and parsing tokens."
        )
