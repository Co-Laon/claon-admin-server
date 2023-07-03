import uuid
from datetime import datetime, timedelta

from jose import jwt

from claon_admin.common.error.exception import UnauthorizedException
from claon_admin.common.error.exception import ErrorCode
from claon_admin.common.util.redis import save_refresh_key
from claon_admin.config.config import conf
from claon_admin.common.consts import TIME_ZONE_KST


def create_access_token(user_id: str) -> str:
    to_encode = {
        "sub": user_id,
        "exp": datetime.now(TIME_ZONE_KST) + timedelta(minutes=conf().ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    return jwt.encode(to_encode, conf().JWT_SECRET_KEY, conf().JWT_ALGORITHM)


def create_refresh_key(user_id: str) -> str:
    refresh_key = str(uuid.uuid4())
    save_refresh_key(refresh_key=refresh_key, user_id=user_id)
    return refresh_key


def resolve_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            conf().JWT_SECRET_KEY,
            algorithms=[conf().JWT_ALGORITHM],
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
