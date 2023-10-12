from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from .common import AdditionalInfo, RequestStatusEnum
from .message import MsgCallbackHeader, MsgHeader


class LinkRequestStatusReasonCode(Enum):
    rjct_reference_id_invalid = "rjct.reference_id.invalid"
    rjct_reference_id_duplicate = "rjct.reference_id.duplicate"
    rjct_timestamp_invalid = "rjct.timestamp.invalid"
    rjct_id_invalid = "rjct.id.invalid"
    rjct_fa_invalid = "rjct.fa.invalid"
    rjct_name_invalid = "rjct.name.invalid"
    rjct_mobile_number_invalid = "rjct.mobile_number.invalid"
    rjct_unknown_retry = "rjct.unknown.retry"
    rjct_other_error = "rjct.other.error"


class SingleLinkRequest(BaseModel):
    reference_id: str
    timestamp: datetime
    id: str
    fa: str
    name: Optional[str] = None
    phone_number: Optional[str] = None
    additional_info: Optional[List[AdditionalInfo]]
    locale: str = "en"


class LinkRequest(BaseModel):
    description: Optional[str] = ""
    transaction_id: str
    link_request: List[SingleLinkRequest]


class LinkHttpRequest(BaseModel):
    signature: str
    header: MsgHeader
    message: LinkRequest


class SingleLinkCallbackRequest(BaseModel):
    reference_id: str
    timestamp: datetime
    fa: str
    status: RequestStatusEnum
    status_reason_code: Optional[LinkRequestStatusReasonCode]
    status_reason_message: Optional[str]
    additional_info: Optional[List[AdditionalInfo]]
    locale: str = "en"


class LinkCallbackRequest(BaseModel):
    description: Optional[str] = ""
    transaction_id: str
    link_response: List[SingleLinkCallbackRequest]


class LinkCallbackHttpRequest(BaseModel):
    signature: str
    header: MsgCallbackHeader
    message: LinkCallbackRequest
