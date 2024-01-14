import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import List

import httpx
import orjson
import redis
import redis.asyncio as redis_asyncio
from openg2p_fastapi_common.errors.base_exception import BaseAppException
from openg2p_fastapi_common.service import BaseService

from ..config import Settings
from ..context import queue_redis_async_pool, queue_redis_conn_pool
from ..models.common import (
    Ack,
    CommonResponseMessage,
    MapperValue,
    RequestStatusEnum,
    SingleTxnRefStatus,
    TxnStatus,
)
from ..models.message import MsgHeader
from ..models.resolve import ResolveHttpRequest, ResolveRequest, SingleResolveRequest

_config = Settings.get_config(strict=False)
_logger = logging.getLogger(_config.logging_default_logger_name)


class MapperResolveService(BaseService):
    async def resolve_request(
        self,
        mappings: List[MapperValue],
        txn_id: str = None,
        wait_for_response: bool = True,
        loop_sleep=1,
        max_retries=10,
    ) -> TxnStatus:
        resolve_http_request, txn_status = self.get_new_resolve_request(
            mappings, txn_id
        )

        queue = redis_asyncio.Redis(connection_pool=queue_redis_async_pool.get())
        await queue.set(
            f"{_config.queue_resolve_name}{txn_status.txn_id}",
            orjson.dumps(txn_status.model_dump()).decode(),
        )

        if not mappings:
            txn_status.status = RequestStatusEnum.succ
            return txn_status

        if not wait_for_response:
            asyncio.create_task(
                self.start_resolve_process(resolve_http_request, txn_status)
            )
            await queue.aclose()
            return txn_status

        await self.start_resolve_process(resolve_http_request, txn_status)

        retry_count = 0
        while retry_count < max_retries:
            res_txn_status = TxnStatus.model_validate(
                orjson.loads(
                    await queue.get(f"{_config.queue_resolve_name}{txn_status.txn_id}")
                )
            )
            if res_txn_status.status in (
                RequestStatusEnum.succ,
                RequestStatusEnum.rjct,
            ):
                await queue.aclose()
                return res_txn_status
            retry_count += 1
            if loop_sleep:
                await asyncio.sleep(loop_sleep)
        await queue.aclose()
        raise BaseAppException("G2P-MAP-101", "Max retries exhausted while resolving.")

    def resolve_request_sync(
        self,
        mappings: List[MapperValue],
        txn_id: str = None,
        loop_sleep=1,
        max_retries=10,
    ) -> TxnStatus:
        resolve_http_request, txn_status = self.get_new_resolve_request(
            mappings, txn_id
        )

        queue = redis.Redis(connection_pool=queue_redis_conn_pool.get())
        queue.set(
            f"{_config.queue_resolve_name}{txn_status.txn_id}",
            orjson.dumps(txn_status.model_dump()).decode(),
        )

        if not mappings:
            txn_status.status = RequestStatusEnum.succ
            queue.close()
            return txn_status

        self.start_resolve_process_sync(resolve_http_request, txn_status)

        retry_count = 0
        while retry_count < max_retries:
            res_txn_status = TxnStatus.model_validate(
                orjson.loads(
                    queue.get(f"{_config.queue_resolve_name}{txn_status.txn_id}")
                )
            )
            if res_txn_status.status in (
                RequestStatusEnum.succ,
                RequestStatusEnum.rjct.value,
            ):
                queue.close()
                return res_txn_status
            retry_count += 1
            if loop_sleep:
                time.sleep(loop_sleep)

        queue.close()
        raise BaseAppException("G2P-MAP-101", "Max retries exhausted while resolving.")

    async def start_resolve_process(
        self, resolve_http_request: ResolveHttpRequest, txn_status: TxnStatus
    ):
        try:
            client = httpx.AsyncClient()
            res = await client.post(
                _config.mapper_resolve_url,
                content=resolve_http_request.model_dump_json(),
                headers={"content-type": "application/json"},
                timeout=_config.mapper_api_timeout_secs,
            )
            await client.aclose()
            res.raise_for_status()
            res = CommonResponseMessage.model_validate(res.json())
            if res.message.ack_status != Ack.ACK:
                _logger.error(
                    "Encountered negative ACK from ID Mapper during resolve request"
                )
                txn_status.change_all_status(RequestStatusEnum.rjct)
            else:
                txn_status.change_all_status(RequestStatusEnum.pdng)
        except httpx.ReadTimeout:
            # TODO: There is a timeout problem with sunbird
            _logger.exception("Encountered timeout during ID Mapper resolve request")
        except Exception:
            _logger.exception("Encountered error during ID Mapper resolve request")
            txn_status.change_all_status(RequestStatusEnum.rjct)

    def start_resolve_process_sync(
        self, resolve_http_request: ResolveHttpRequest, txn_status: TxnStatus
    ):
        try:
            res = httpx.post(
                _config.mapper_resolve_url,
                content=resolve_http_request.model_dump_json(),
                headers={"content-type": "application/json"},
                timeout=_config.mapper_api_timeout_secs,
            )
            res.raise_for_status()
            res = CommonResponseMessage.model_validate(res.json())
            if res.message.ack_status != Ack.ACK:
                _logger.error(
                    "Encountered negative ACK from ID Mapper during resolve request"
                )
                txn_status.change_all_status(RequestStatusEnum.rjct)
            else:
                txn_status.change_all_status(RequestStatusEnum.pdng)
        except httpx.ReadTimeout:
            # TODO: There is a timeout problem with sunbird
            _logger.exception("Encountered timeout during ID Mapper resolve request")
        except Exception:
            _logger.exception("Encountered error during ID Mapper resolve request")
            txn_status.change_all_status(RequestStatusEnum.rjct)

    def get_new_resolve_request(
        self,
        mappings: List[MapperValue],
        txn_id: str = None,
    ):
        current_timestamp = datetime.utcnow()

        resolve_request = []
        txn_statuses = {}
        total_count = len(mappings)

        if not txn_id:
            txn_id = str(uuid.uuid4())
        for mapping in mappings:
            reference_id = str(uuid.uuid4())
            txn_statuses[reference_id] = SingleTxnRefStatus(
                status=RequestStatusEnum.rcvd,
                reference_id=reference_id,
                **mapping.model_dump(),
            )
            single_resolve_request = SingleResolveRequest(
                reference_id=reference_id,
                timestamp=current_timestamp,
            )
            if mapping.id:
                single_resolve_request.id = mapping.id
            if mapping.fa:
                single_resolve_request.fa = mapping.fa
            else:
                # TODO: raise error if neither id nor fa present
                pass
            resolve_request.append(single_resolve_request)

        txn_status = TxnStatus(
            txn_id=txn_id,
            status=RequestStatusEnum.rcvd,
            refs=txn_statuses,
        )

        resolve_http_request = (
            ResolveHttpRequest(
                signature='Signature:  namespace="g2p", '
                'kidId="{sender_id}|{unique_key_id}|{algorithm}", '
                'algorithm="ed25519", created="1606970629", '
                'expires="1607030629", '
                'headers="(created) '
                '(expires) digest", '
                'signature="Base64(signing content)',
                header=MsgHeader(
                    message_id=str(uuid.uuid4()),
                    message_ts=current_timestamp,
                    action="resolve",
                    sender_id=_config.mapper_common_sender_id,
                    sender_uri=_config.mapper_resolve_sender_url,
                    total_count=total_count,
                ),
                message=ResolveRequest(
                    transaction_id=txn_id, resolve_request=resolve_request
                ),
            )
            if mappings
            else None
        )

        return resolve_http_request, txn_status
