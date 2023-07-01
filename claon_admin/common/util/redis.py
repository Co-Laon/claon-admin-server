from claon_admin.config.config import conf
from claon_admin.config.redis import redis


def save_refresh_key(refresh_key: str, user_id: str):
    with redis.get_connection() as conn:
        conn.set(refresh_key, user_id, ex=conf().REFRESH_TOKEN_EXPIRE_MINUTES * 60)


def delete_refresh_key(refresh_key: str):
    with redis.get_connection() as conn:
        if conn.get(refresh_key) is not None:
            conn.delete(refresh_key)


def find_user_id_by_refresh_key(refresh_key: str) -> str | None:
    with redis.get_connection() as conn:
        return conn.get(refresh_key)
