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
    description: Optional[str] = ""
    name: str
    code: str
    subcode: str
    additional_info: str


class AdditionalInfo(BaseModel):
    description: Optional[str] = ""
    name: str
    value: Union[int, float, str, bool, dict]


class RequestStatusEnum(Enum):
    rcvd = "rcvd"
    pdng = "pdng"
    succ = "succ"
    rjct = "rjct"


class CommonResponse(BaseModel):
    ack_status: Ack
    timestamp: datetime
    error: Optional[ErrorResponse]
    correlation_id: str


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
    callable_on_complete: Callable[["TxnStatus"], Coroutine] = None

    def change_all_status(self, status: RequestStatusEnum):
        self.status = status
        for ref in self.refs:
            self.refs[ref].status = status
