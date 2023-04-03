from datetime import datetime, timedelta, timezone

from fastapi import Header, Depends
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.error.exception import UnauthorizedException
from claon_admin.common.error.exception import ErrorCode
from claon_admin.config.consts import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, JWT_SECRET_KEY, \
    REFRESH_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_SECRET_KEY, TIME_ZONE_KST
from claon_admin.container import db
from claon_admin.schema.jwtsample import UserRepository


def create_access_token(nickname: str) -> str:
    to_encode = {"sub": nickname}

    expire = datetime.now(TIME_ZONE_KST) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)

    return encoded_jwt


def create_refresh_token(nickname: str) -> str:
    to_encode = {"sub": nickname}

    expire = datetime.now(TIME_ZONE_KST) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)

    return encoded_jwt


def is_expired(payload: dict):
    if datetime.now(TIME_ZONE_KST) > datetime.fromtimestamp(payload.get("exp"), TIME_ZONE_KST):
        return True
    return False


async def do_jwt_authentication(
        access_token: str = Header(None),
        refresh_token: str = Header(None),
        session: AsyncSession = Depends(db.get_db)
) -> dict:
    try:
        if access_token is None:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "Cannot find access token from request header."
            )

        if refresh_token is None:
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "Cannot find refresh token from request header."
            )

        access_payload = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        refresh_payload = jwt.decode(refresh_token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})

        if not await UserRepository.find_by_nickname(session, access_payload.get("sub")):
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "Not existing user account."
            )

        if is_expired(access_payload):
            if is_expired(refresh_payload):
                raise UnauthorizedException(
                    ErrorCode.NOT_ACCESSIBLE,
                    "Both access token and refresh token are expired."
                )
            access_token = create_access_token(access_payload.get("sub"))
            return {"access-token": access_token, "refresh-token": refresh_token}
        else:
            if is_expired(refresh_payload):
                raise UnauthorizedException(
                    ErrorCode.NOT_ACCESSIBLE,
                    "Refresh token is expired."
                )
            return {"access-token": access_token, "refresh-token": refresh_token}

    except ValueError:
        raise UnauthorizedException(
            ErrorCode.NOT_ACCESSIBLE,
            "Related headers are not valid."
        )
