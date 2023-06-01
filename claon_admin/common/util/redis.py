from claon_admin.config.config import conf
from claon_admin.config.redis import redis


def save_refresh_token(refresh_token: str, user_id: str):
    with redis.get_connection() as conn:
        conn.set(refresh_token, user_id, ex=conf().REFRESH_TOKEN_EXPIRE_MINUTES * 60)


def delete_refresh_token(refresh_token: str):
    with redis.get_connection() as conn:
        if conn.get(refresh_token) is not None:
            conn.delete(refresh_token)


def find_user_id_by_refresh_token(refresh_token: str) -> str | None:
    with redis.get_connection() as conn:
        return conn.get(refresh_token)
