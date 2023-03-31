from datetime import datetime, timedelta, timezone

from fastapi import Header
from jose import jwt

from claon_admin.common.error.exception import UnauthorizedException
from claon_admin.common.error.exception import ErrorCode
from claon_admin.config.consts import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, JWT_SECRET_KEY, \
    REFRESH_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_SECRET_KEY


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)

    return encoded_jwt


def is_expired(payload: dict):
    if datetime.now(timezone.utc) > datetime.fromtimestamp(payload.get("exp"), timezone.utc):
        return True
    return False


async def do_jwt_filter(
        authorization: str = Header(None)
) -> dict:

    if authorization is None:
        raise UnauthorizedException(
            ErrorCode.NOT_ACCESSIBLE,
            "Authorization 헤더가 비어있습니다."
        )

    try:
        auth_type, tokens = authorization.split(" ")

        if auth_type.lower() != "bearer":
            raise UnauthorizedException(
                ErrorCode.NOT_ACCESSIBLE,
                "토큰 헤더의 타입이 잘못되었습니다."
            )
        else:
            access_token, refresh_token = tokens.split(":")

            if access_token is None or refresh_token is None:
                raise UnauthorizedException(
                    ErrorCode.NOT_ACCESSIBLE,
                    "토큰을 찾을 수 없습니다."
                )

            access_payload = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
            refresh_payload = jwt.decode(refresh_token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})

            # handle 2 by 2 cases
            if is_expired(access_payload):
                if is_expired(refresh_payload):
                    raise UnauthorizedException(
                        ErrorCode.NOT_ACCESSIBLE,
                        "모든 토큰이 만료되었습니다."
                    )
                else:
                    access_token = create_access_token({})
                    return {"access-token": access_token, "refresh-token": refresh_token}
            else:
                if is_expired(refresh_payload):
                    refresh_token = create_refresh_token({})
                    return {"access-token": access_token, "refresh-token": refresh_token}
                else:
                    return {"access-token": access_token, "refresh-token": refresh_token}

    except ValueError:
        raise UnauthorizedException(
            ErrorCode.NOT_ACCESSIBLE,
            "Authorization 헤더의 형식이 올바르지 않습니다."
        )
