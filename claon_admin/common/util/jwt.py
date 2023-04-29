from datetime import datetime, timedelta

from jose import jwt

from claon_admin.common.error.exception import UnauthorizedException
from claon_admin.common.error.exception import ErrorCode
from claon_admin.common.util.redis import save_refresh_token, delete_refresh_token
from claon_admin.config.config import conf
from claon_admin.config.consts import TIME_ZONE_KST


def create_access_token(user_id: str) -> str:
    to_encode = {
        "sub": user_id,
        "exp": datetime.now(TIME_ZONE_KST) + timedelta(minutes=conf().ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    return jwt.encode(to_encode, conf().JWT_SECRET_KEY, conf().JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    to_encode = {
        "exp": datetime.now(TIME_ZONE_KST) + timedelta(minutes=conf().REFRESH_TOKEN_EXPIRE_MINUTES)
    }

    token = jwt.encode(to_encode, conf().JWT_REFRESH_SECRET_KEY, conf().JWT_ALGORITHM)
    save_refresh_token(token, user_id)
    return token


def reissue_refresh_token(refresh_token: str, user_id: str) -> str:
    delete_refresh_token(refresh_token)
    return create_refresh_token(user_id)


def resolve_access_token(access_token: str) -> dict:
    try:
        return jwt.decode(
            access_token,
            conf().JWT_SECRET_KEY,
            algorithms=[conf().JWT_ALGORITHM],
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
            conf().JWT_REFRESH_SECRET_KEY,
            algorithms=[conf().JWT_ALGORITHM],
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
