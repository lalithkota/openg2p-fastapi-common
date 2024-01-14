from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from openg2p_fastapi_common.errors import ErrorResponse
from pydantic import AliasChoices, BaseModel, Field, field_validator


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
    name: str = Field(validation_alias=AliasChoices("name", "key"))
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

    def change_all_status(self, status: RequestStatusEnum):
        self.status = status
        for ref in self.refs:
            self.refs[ref].status = status


class SingleCommonRequest(BaseModel):
    reference_id: str
    timestamp: datetime
    additional_info: Optional[Union[List[AdditionalInfo], AdditionalInfo]] = None
    locale: str = "eng"

    @field_validator("additional_info")
    @classmethod
    def convert_addl_info_dict_list(
        cls, v: Optional[Union[List[AdditionalInfo], AdditionalInfo]]
    ):
        if not isinstance(v, list):
            v = [v]
        return v
