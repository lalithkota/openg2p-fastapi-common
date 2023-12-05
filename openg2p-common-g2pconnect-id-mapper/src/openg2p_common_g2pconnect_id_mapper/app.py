# ruff: noqa: E402

import redis
import redis.asyncio as redis_asyncio
from fastapi import FastAPI

from .config import Settings

_config = Settings.get_config(strict=False)

from openg2p_fastapi_common.app import Initializer

from .context import (
    queue_redis_async_pool,
    queue_redis_conn_pool,
)
from .controllers.link_callback import LinkCallbackController
from .controllers.resolve_callback import ResolveCallbackController
from .controllers.update_callback import UpdateCallbackController
from .service.link import MapperLinkService
from .service.resolve import MapperResolveService
from .service.update import MapperUpdateService


class Initializer(Initializer):
    def initialize(self, **kwargs):
        # Initialize all Services, Controllers, any utils here.
        self.init_queue_redis_pools()

        MapperResolveService()
        MapperLinkService()
        MapperUpdateService()

        LinkCallbackController().post_init()
        UpdateCallbackController().post_init()
        ResolveCallbackController().post_init()

    def init_queue_redis_pools(self):
        queue_redis_conn_pool.set(
            redis.ConnectionPool.from_url(_config.queue_redis_source)
        )
        queue_redis_async_pool.set(
            redis_asyncio.ConnectionPool.from_url(_config.queue_redis_source)
        )

    async def fastapi_app_shutdown(self, app: FastAPI):
        if queue_redis_conn_pool.get():
            queue_redis_conn_pool.get().close()
            queue_redis_conn_pool.set(None)
        if queue_redis_async_pool.get():
            await queue_redis_async_pool.get().aclose()
            queue_redis_async_pool.set(None)
