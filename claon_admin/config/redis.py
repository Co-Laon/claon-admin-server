import redis


class Redis:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_connection(self):
        return redis.StrictRedis(host=self.host, port=self.port, db=0)
