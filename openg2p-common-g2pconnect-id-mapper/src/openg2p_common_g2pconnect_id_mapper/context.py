from contextvars import ContextVar
from typing import Callable, Dict

import redis
import redis.asyncio as redis_asyncio

queue_redis_conn_pool: ContextVar[redis.ConnectionPool] = ContextVar(
    "queue_redis_conn_pool", default=None
)
queue_redis_async_pool: ContextVar[redis_asyncio.ConnectionPool] = ContextVar(
    "queue_redis_async_pool", default=None
)

queue_registered_callbacks: ContextVar[Dict[str, Callable]] = ContextVar(
    "queue_registered_callbacks", default=None
)
