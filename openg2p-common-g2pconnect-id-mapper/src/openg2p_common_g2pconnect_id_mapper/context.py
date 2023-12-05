from contextvars import ContextVar

import redis
import redis.asyncio as redis_asyncio

queue_redis_conn_pool: ContextVar[redis.ConnectionPool] = ContextVar(
    "queue_redis_conn_pool", default=None
)
queue_redis_async_pool: ContextVar[redis_asyncio.ConnectionPool] = ContextVar(
    "queue_redis_async_pool", default=None
)
