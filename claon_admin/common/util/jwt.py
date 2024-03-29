import uuid
from datetime import datetime, timedelta

from jose import jwt

from claon_admin.common.error.exception import UnauthorizedException
from claon_admin.common.error.exception import ErrorCode
from claon_admin.common.util.redis import save_refresh_key
from claon_admin.common.consts import TIME_ZONE_KST
from claon_admin.config.env import config

ACCESS_TOKEN_EXPIRE_MINUTES = config.get("security.jwt.expire.access")
JWT_ALGORITHM = config.get("security.jwt.algorithm")
JWT_SECRET_KEY = config.get("security.jwt.secret-key")


def create_access_token(user_id: str) -> str:
    to_encode = {
        "sub": user_id,
        "exp": datetime.now(TIME_ZONE_KST) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    return jwt.encode(to_encode, JWT_SECRET_KEY, JWT_ALGORITHM)


def create_refresh_key(user_id: str) -> str:
    refresh_key = str(uuid.uuid4())
    save_refresh_key(refresh_key=refresh_key, user_id=user_id)
    return refresh_key


def resolve_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as e:
        raise UnauthorizedException(
            ErrorCode.EXPIRED_JWT,
            "token is expired."
        ) from e
    except jwt.JWTError as e:
        raise UnauthorizedException(
            ErrorCode.INVALID_JWT,
            "Invalid token."
        ) from e
