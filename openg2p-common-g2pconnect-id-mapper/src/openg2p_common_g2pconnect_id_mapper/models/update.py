from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from .common import RequestStatusEnum, SingleCommonRequest
from .message import MsgCallbackHeader, MsgHeader


class UpdateRequestStatusReasonCode(Enum):
    rjct_reference_id_invalid = "rjct.reference_id.invalid"
    rjct_reference_id_duplicate = "rjct.reference_id.duplicate"
    rjct_timestamp_invalid = "rjct.timestamp.invalid"
    rjct_beneficiary_name_invalid = "rjct.beneficiary_name.invalid"


class SingleUpdateRequest(SingleCommonRequest):
    id: str
    fa: str
    name: Optional[str] = None
    phone_number: Optional[str] = None


class UpdateRequest(BaseModel):
    transaction_id: str
    update_request: List[SingleUpdateRequest]


class UpdateHttpRequest(BaseModel):
    signature: str
    header: MsgHeader
    message: UpdateRequest


class SingleUpdateCallbackRequest(SingleCommonRequest):
    id: Optional[str] = ""
    status: RequestStatusEnum
    status_reason_code: Optional[UpdateRequestStatusReasonCode] = None
    status_reason_message: Optional[str] = ""


class UpdateCallbackRequest(BaseModel):
    transaction_id: str
    correlation_id: Optional[str] = ""
    update_response: List[SingleUpdateCallbackRequest]


class UpdateCallbackHttpRequest(BaseModel):
    signature: str
    header: MsgCallbackHeader
    message: UpdateCallbackRequest
