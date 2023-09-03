import redis.asyncio as redis

from PhotoShare.app.core.config import settings


class RedisService:
    rds = None

    @classmethod
    async def init(cls):
        RedisService.rds = await redis.Redis(host=settings.redis_host, port=settings.redis_port,
                                             db=0, encoding="utf-8", decode_responses=False)
        return RedisService.rds

    @classmethod
    async def get_redis(cls):
        return RedisService.rds
