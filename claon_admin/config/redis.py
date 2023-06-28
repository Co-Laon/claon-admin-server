import redis as redis_client

from claon_admin.config.config import conf


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
if conf().REDIS_ENABLE:
    redis = RedisClient(host=conf().REDIS_HOST, port=conf().REDIS_PORT)
