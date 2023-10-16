from datetime import datetime
from enum import Enum
from typing import Callable, Coroutine, Dict, Optional, Union

from openg2p_fastapi_common.errors import ErrorResponse
from pydantic import BaseModel


class Ack(Enum):
    ACK = "ACK"
    NACK = "NACK"
    ERR = "ERR"


class AccountProviderInfo(BaseModel):
    name: str
    code: str
    subcode: Optional[str] = ""
    additional_info: Optional[str] = ""


class AdditionalInfo(BaseModel):
    key: str
    value: Union[int, float, str, bool, dict]


class RequestStatusEnum(Enum):
    rcvd = "rcvd"
    pdng = "pdng"
    succ = "succ"
    rjct = "rjct"


class CommonResponse(BaseModel):
    # TODO: Not compatible with G2P Connect
    # ack_status: Ack
    ack_status: Optional[Ack] = None
    timestamp: datetime
    error: Optional[ErrorResponse] = None
    # TODO: Not compatible with G2P Connect
    # correlation_id: str
    correlation_id: Optional[str] = None


class CommonResponseMessage(BaseModel):
    message: CommonResponse


class MapperValue(BaseModel):
    id: Optional[str] = None
    fa: Optional[str] = None


class SingleTxnRefStatus(MapperValue):
    reference_id: str
    status: RequestStatusEnum


class TxnStatus(BaseModel):
    txn_id: str
    status: RequestStatusEnum
    refs: Dict[str, SingleTxnRefStatus]
    callable_on_complete: Optional[Callable[["TxnStatus"], Coroutine]] = None

    def change_all_status(self, status: RequestStatusEnum):
        self.status = status
        for ref in self.refs:
            self.refs[ref].status = status
