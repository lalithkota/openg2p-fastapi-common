import asyncio
import logging
import uuid
from datetime import datetime

from openg2p_fastapi_common.controller import BaseController
from openg2p_fastapi_common.errors.base_error import ErrorResponse

from ..config import Settings
from ..models.common import Ack, CommonResponse, CommonResponseMessage
from ..models.resolve import ResolveCallbackHttpRequest
from ..service.resolve import MapperResolveService

_config = Settings.get_config(strict=False)
_logger = logging.getLogger(__name__)


class ResolveCallbackController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mapper_resolve_service = MapperResolveService.get_component()

        self.router.prefix += _config.callback_api_common_prefix
        self.router.tags += ["callback"]

        self.router.add_api_route(
            "/mapper/on-resolve",
            self.mapper_on_resolve,
            methods=["POST"],
            responses={200: {"model": CommonResponseMessage}},
        )

    async def mapper_on_resolve(self, resolve_http_request: ResolveCallbackHttpRequest):
        txn_id = resolve_http_request.message.transaction_id
        txn_status = self.mapper_resolve_service.transaction_queue.get(txn_id, None)
        if not txn_status:
            _logger.error("On resolve. Invalid Txn id received.")
            return CommonResponseMessage(
                message=CommonResponse(
                    ack_status=Ack.NACK,
                    timestamp=datetime.utcnow(),
                    correlation_id=str(uuid.uuid4()),
                    error=ErrorResponse(
                        code="rjct.transaction.id.invalid",
                        message="Unknown transaction id.",
                    ),
                )
            )
        txn_status.status = resolve_http_request.header.status

        for txn in resolve_http_request.message.resolve_response:
            txn_status.refs[txn.reference_id].status = txn.status
            if txn.status_reason_code:
                _logger.error(
                    "On Resolve. Error Received on callback, code: %s, message: %s",
                    txn.status_reason_code,
                    txn.status_reason_message,
                )
                continue
            if txn.fa:
                txn_status.refs[txn.reference_id].fa = txn.fa
            if txn.id:
                txn_status.refs[txn.reference_id].id = txn.id

        if txn_status.callable_on_complete:
            asyncio.create_task(txn_status.callable_on_complete(txn_status))

        return CommonResponseMessage(
            message=CommonResponse(
                ack_status=Ack.ACK,
                timestamp=datetime.utcnow(),
                correlation_id=str(uuid.uuid4()),
            )
        )
