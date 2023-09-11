import redis

from PhotoShare.app.core.config import settings


class RedisService:
    rds = None

    @classmethod
    def init(cls):
        RedisService.rds = redis.Redis(host=settings.redis_host, port=settings.redis_port,
                                       password=settings.redis_password, db=0, encoding="utf-8")
        return RedisService.rds

    @classmethod
    def get_redis(cls):
        return RedisService.rds
