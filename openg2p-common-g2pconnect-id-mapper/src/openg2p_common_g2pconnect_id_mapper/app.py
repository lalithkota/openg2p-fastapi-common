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
    queue_registered_callbacks,
)
from .controllers.link_callback import LinkCallbackController
from .controllers.resolve_callback import ResolveCallbackController
from .controllers.update_callback import UpdateCallbackController
from .service.link import MapperLinkService
from .service.resolve import MapperResolveService
from .service.update import MapperUpdateService
from .service.update_link import MapperUpdateOrLinkService


class Initializer(Initializer):
    def initialize(self, **kwargs):
        # Initialize all Services, Controllers, any utils here.
        self.init_queue_redis_pools()

        MapperResolveService()
        MapperLinkService()
        MapperUpdateService()
        self.mapper_update_link_service = MapperUpdateOrLinkService()

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

    def register_callbacks(self):
        callback_func = (
            self.mapper_update_link_service.update_link_service_on_link_callback
        )
        callback_name = callback_func.__name__
        queue_registered_callbacks.get()[callback_name] = callback_func

        callback_func = (
            self.mapper_update_link_service.update_link_service_on_update_callback
        )
        callback_name = callback_func.__name__
        queue_registered_callbacks.get()[callback_name] = callback_func

        callback_func = (
            self.mapper_update_link_service.update_link_service_on_resolve_callback
        )
        callback_name = callback_func.__name__
        queue_registered_callbacks.get()[callback_name] = callback_func
