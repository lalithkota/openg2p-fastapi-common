import asyncio
import logging
from typing import Callable, Coroutine, Dict, List

from openg2p_fastapi_common.errors.base_exception import BaseAppException
from openg2p_fastapi_common.service import BaseService

from ..config import Settings
from ..models.common import MapperValue, RequestStatusEnum, TxnStatus
from ..service.link import MapperLinkService
from ..service.resolve import MapperResolveService
from ..service.update import MapperUpdateService

_logger = logging.getLogger(__name__)
_config = Settings.get_config(strict=False)


class MapperUpdateOrLinkService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: Do garbage collection for this
        self.transaction_queue: Dict[str, TxnStatus] = {}

        self.mapper_update_service = MapperUpdateService.get_component()
        self.mapper_link_service = MapperLinkService.get_component()
        self.mapper_resolve_service = MapperResolveService.get_component()

    async def update_or_link_request(
        self,
        mappings: List[MapperValue],
        callback_func: Callable[[TxnStatus], Coroutine] = None,
    ) -> TxnStatus:
        async def on_resolve_callback(resolve_txn_status: TxnStatus):
            to_link_mappings = []
            to_update_mappings = []
            for txn in resolve_txn_status.refs.values():
                mapper_value = next(
                    (m for m in mappings if m.id and m.id == txn.id), None
                )
                if not mapper_value:
                    raise BaseAppException(
                        "G2P-GCI-300", "Something went wrong. ID not found in txn list"
                    )
                if not (txn.status == RequestStatusEnum.succ and txn.fa):
                    # TODO: Also check reason for this failure
                    to_link_mappings.append(mapper_value)
                else:
                    to_update_mappings.append(mapper_value)

            async def on_link_callback(link_txn_status: TxnStatus):
                async def on_update_callback(update_txn_status: TxnStatus):
                    # TODO: Improve the following logic of merge update records and link records
                    final_txn_status = update_txn_status.model_copy()
                    final_txn_status.refs.update(link_txn_status.refs)
                    final_txn_status.txn_id = resolve_txn_status.txn_id

                    self.transaction_queue[final_txn_status.txn_id] = final_txn_status

                    if callback_func:
                        asyncio.create_task(callback_func(final_txn_status))

                await self.mapper_update_service.update_request(
                    to_update_mappings, on_update_callback
                )

            await self.mapper_link_service.link_request(
                to_link_mappings, on_link_callback
            )

        res = await self.mapper_resolve_service.resolve_request(
            mappings, on_resolve_callback
        )
        self.transaction_queue[res.txn_id] = res
        return res
