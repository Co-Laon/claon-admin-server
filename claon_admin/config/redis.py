import redis as redis_client

from claon_admin.config.env import config

REDIS_ENABLE = config.get("redis.enable")
REDIS_HOST = config.get("redis.host")
REDIS_PORT = config.get("redis.port")


class RedisClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_connection(self):
        return redis_client.StrictRedis(
            host=self.host,
            port=self.port,
            db=0,
            charset="utf-8",
            decode_responses=True,
        )


redis = None
if REDIS_ENABLE:
    redis = RedisClient(host=REDIS_HOST, port=REDIS_PORT)
