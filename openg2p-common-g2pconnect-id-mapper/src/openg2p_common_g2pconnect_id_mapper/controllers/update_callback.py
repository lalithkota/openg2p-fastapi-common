import asyncio
import logging
import uuid
from datetime import datetime

from openg2p_fastapi_common.controller import BaseController
from openg2p_fastapi_common.errors.base_error import ErrorResponse

from ..config import Settings
from ..models.common import Ack, CommonResponse, CommonResponseMessage
from ..models.update import UpdateCallbackHttpRequest
from ..service.update import MapperUpdateService

_config = Settings.get_config(strict=False)
_logger = logging.getLogger(__name__)


class UpdateCallbackController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mapper_update_service = MapperUpdateService.get_component()

        self.router.prefix += _config.callback_api_common_prefix
        self.router.tags += ["callback"]

        self.router.add_api_route(
            "/mapper/on-update",
            self.mapper_on_update,
            methods=["POST"],
            responses={200: {"model": CommonResponseMessage}},
        )

    async def mapper_on_update(self, update_http_request: UpdateCallbackHttpRequest):
        txn_id = update_http_request.message.transaction_id
        txn_status = self.mapper_update_service.transaction_queue.get(txn_id, None)
        if not txn_status:
            _logger.error("On Update. Invalid Txn id received.")
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
        txn_status.status = update_http_request.header.status

        for txn in update_http_request.message.update_response:
            txn_status.refs[txn.reference_id].status = txn.status
            if txn.status_reason_code:
                _logger.error(
                    "On Update. Error Received on callback, code: %s, message: %s",
                    txn.status_reason_code,
                    txn.status_reason_message,
                )
                continue

        if txn_status.callable_on_complete:
            asyncio.create_task(txn_status.callable_on_complete(txn_status))

        return CommonResponseMessage(
            message=CommonResponse(
                ack_status=Ack.ACK,
                timestamp=datetime.utcnow(),
                correlation_id=str(uuid.uuid4()),
            )
        )
