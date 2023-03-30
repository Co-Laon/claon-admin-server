from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Header
from jose import jwt
from passlib.context import CryptContext
from starlette import status

from claon_admin.config.consts import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, JWT_SECRET_KEY, \
    REFRESH_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_SECRET_KEY

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)

    return encoded_jwt


def is_expired(payload: dict):
    print("****************")
    print(datetime.now(timezone.utc))
    print(datetime.fromtimestamp(payload.get("exp"), timezone.utc))
    if datetime.now(timezone.utc) > datetime.fromtimestamp(payload.get("exp"), timezone.utc):
        return True
    return False


async def get_token_from_header(
        authorization: str = Header(None)
) -> str:
    try:
        auth_type, tokens = authorization.split(" ")
        if auth_type.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰 헤더가 잘못되었습니다."
            )
        else:
            return tokens
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰의 형식이 잘못되었습니다."
        )


async def do_authentication_filter(
        tokens: str = Depends(get_token_from_header)
) -> dict:
    access_token, refresh_token = tokens.split(":")
    if access_token is None or refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰을 찾을 수 없습니다."
        )

    access_payload = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
    refresh_payload = jwt.decode(refresh_token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})

    if is_expired(access_payload):
        if is_expired(refresh_payload):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다."
            )
        else:
            return refresh_payload
    else:
        return access_payload
