import asyncio
import logging
import uuid
from typing import Callable, Coroutine, List

import orjson
import redis.asyncio as redis_asyncio
from openg2p_fastapi_common.errors.base_exception import BaseAppException
from openg2p_fastapi_common.service import BaseService

from ..config import Settings
from ..context import queue_redis_async_pool, queue_registered_callbacks
from ..models.common import (
    MapperValue,
    RequestStatusEnum,
    SingleTxnRefStatus,
    TxnStatus,
)
from ..service.link import MapperLinkService
from ..service.resolve import MapperResolveService
from ..service.update import MapperUpdateService

_logger = logging.getLogger(__name__)
_config = Settings.get_config(strict=False)


class MapperUpdateOrLinkService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mapper_update_service = MapperUpdateService.get_component()
        self.mapper_link_service = MapperLinkService.get_component()
        self.mapper_resolve_service = MapperResolveService.get_component()

    def get_new_update_link_request(
        self,
        mappings: List[MapperValue],
        callback_func: Callable[[TxnStatus], Coroutine] = None,
        txn_id: str = None,
    ):
        txn_statuses = {}

        if not txn_id:
            txn_id = str(uuid.uuid4())
        for mapping in mappings:
            reference_id = str(uuid.uuid4())
            txn_statuses[reference_id] = SingleTxnRefStatus(
                status=RequestStatusEnum.rcvd,
                reference_id=reference_id,
                **mapping.model_dump(),
            )
        txn_status = TxnStatus(
            txn_id=txn_id,
            status=RequestStatusEnum.rcvd,
            refs=txn_statuses,
            callable_on_complete=callback_func.__name__ if callback_func else None,
        )

        return None, txn_status

    async def update_or_link_request(
        self,
        mappings: List[MapperValue],
        callback_func: Callable[[TxnStatus], Coroutine] = None,
        txn_id: str = None,
    ) -> TxnStatus:
        # TODO: This fails when two mappings from list have same ID.
        # So throw error if any two mappings have same ID.

        _, txn_status = self.get_new_update_link_request(
            mappings, callback_func, txn_id
        )

        queue = redis_asyncio.Redis(connection_pool=queue_redis_async_pool.get())
        await queue.set(
            f"{_config.queue_update_link_name}{txn_status.txn_id}",
            orjson.dumps(txn_status.model_dump()).decode(),
        )
        await queue.aclose()

        if not mappings:
            txn_status.status = RequestStatusEnum.succ
            if callback_func:
                asyncio.create_task(callback_func(txn_status))
            return txn_status

        asyncio.create_task(
            self.mapper_resolve_service.resolve_request(
                mappings,
                self.update_link_service_on_resolve_callback,
                txn_status.txn_id,
            )
        )
        return txn_status

    async def update_link_service_on_resolve_callback(
        self, resolve_txn_status: TxnStatus
    ):
        to_link_mappings = []
        for txn in resolve_txn_status.refs.values():
            if not (txn.status == RequestStatusEnum.succ and txn.fa):
                # TODO: Also check reason for this failure
                to_link_mappings.append(txn)

        await self.mapper_link_service.link_request(
            to_link_mappings,
            self.update_link_service_on_link_callback,
            resolve_txn_status.txn_id,
        )

    async def update_link_service_on_link_callback(self, link_txn_status: TxnStatus):
        queue = redis_asyncio.Redis(connection_pool=queue_redis_async_pool)
        resolve_txn_status = TxnStatus.model_validate(
            orjson.loads(
                await queue.get(f"{_config.queue_resolve_name}{link_txn_status.txn_id}")
            )
        )
        await queue.aclose()

        to_update_mappings = []
        for txn in resolve_txn_status.refs.values():
            if txn.status == RequestStatusEnum.succ and txn.fa:
                to_update_mappings.append(txn)

        await self.mapper_update_service.update_request(
            to_update_mappings,
            self.update_link_service_on_update_callback,
            link_txn_status.txn_id,
        )

    async def update_link_service_on_update_callback(
        self, update_txn_status: TxnStatus
    ):
        queue = redis_asyncio.Redis(connection_pool=queue_redis_async_pool)
        update_link_txn_status = TxnStatus.model_validate(
            orjson.loads(
                await queue.get(
                    f"{_config.queue_update_link_name}{update_txn_status.txn_id}"
                )
            )
        )
        resolve_txn_status = TxnStatus.model_validate(
            orjson.loads(
                await queue.get(
                    f"{_config.queue_resolve_name}{update_txn_status.txn_id}"
                )
            )
        )
        link_txn_status = TxnStatus.model_validate(
            orjson.loads(
                await queue.get(f"{_config.queue_link_name}{update_txn_status.txn_id}")
            )
        )
        await queue.aclose()

        for ref in update_link_txn_status.refs.values():
            for resolve_ref in resolve_txn_status.refs.values():
                if resolve_ref.id == ref.id:
                    if resolve_ref.status == RequestStatusEnum.succ:
                        status_to_search = update_txn_status
                    else:
                        # TODO: Also check reason for this failure
                        status_to_search = link_txn_status
                    for j_ref in status_to_search.refs.values():
                        if j_ref.id == ref.id:
                            ref.status = j_ref.status
                            break
                    break

        success_count = 0
        pending_count = 0
        for ref in update_link_txn_status.refs.values():
            if ref.status not in (RequestStatusEnum.succ, RequestStatusEnum.rjct):
                pending_count += 1
            if ref.status == RequestStatusEnum.succ:
                success_count += 1
        if success_count == 0 and pending_count == 0:
            update_link_txn_status.status = RequestStatusEnum.rjct
        elif pending_count == 0:
            update_link_txn_status.status = RequestStatusEnum.succ
        else:
            # TODO: Something went wrong. Pending count can not be > 0
            pass

        if update_link_txn_status.callable_on_complete:
            callback_func = queue_registered_callbacks.get().get(
                update_link_txn_status.callable_on_complete, None
            )
            if not callback_func:
                raise BaseAppException(
                    "G2P-MAP-120",
                    "Invalid Callback Function. Callback function needs to be registered.",
                )
            asyncio.create_task(callback_func(update_link_txn_status))
