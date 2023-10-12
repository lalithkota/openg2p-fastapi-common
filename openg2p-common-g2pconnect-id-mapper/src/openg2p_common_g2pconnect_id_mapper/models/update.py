from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .common import AdditionalInfo, RequestStatusEnum
from .message import MsgCallbackHeader, MsgHeader


class UpdateRequestStatusReasonCode(BaseModel):
    rjct_reference_id_invalid = "rjct.reference_id.invalid"
    rjct_reference_id_duplicate = "rjct.reference_id.duplicate"
    rjct_timestamp_invalid = "rjct.timestamp.invalid"
    rjct_beneficiary_name_invalid = "rjct.beneficiary_name.invalid"


class SingleUpdateRequest(BaseModel):
    reference_id: str
    timestamp: datetime
    id: str
    fa: str
    name: Optional[str]
    phone_number: Optional[str]
    additional_info: Optional[List[AdditionalInfo]]
    locale: str = "en"


class UpdateRequest(BaseModel):
    description: Optional[str]
    transaction_id: str
    update_request: List[SingleUpdateRequest]


class UpdateHttpRequest(BaseModel):
    signature: str
    header: MsgHeader
    message: UpdateRequest


class SingleUpdateCallbackRequest(BaseModel):
    reference_id: str
    timestamp: datetime
    id: Optional[str] = None
    status: RequestStatusEnum
    status_reason_code: Optional[UpdateRequestStatusReasonCode]
    status_reason_message: Optional[str]
    additional_info: Optional[List[AdditionalInfo]]
    locale: str = "en"


class UpdateCallbackRequest(BaseModel):
    description: Optional[str]
    transaction_id: str
    correlation_id: str
    update_response: List[SingleUpdateCallbackRequest]


class UpdateCallbackHttpRequest(BaseModel):
    signature: str
    header: MsgCallbackHeader
    message: UpdateCallbackRequest
