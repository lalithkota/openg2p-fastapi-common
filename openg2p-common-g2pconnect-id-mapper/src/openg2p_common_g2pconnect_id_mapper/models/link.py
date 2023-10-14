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
    # TODO: Not compatible with G2P Connect
    # additional_info: Optional[List[AdditionalInfo]] = []
    additional_info: Optional[AdditionalInfo] = None
    locale: str = "eng"


class LinkRequest(BaseModel):
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
    status_reason_code: Optional[LinkRequestStatusReasonCode] = None
    status_reason_message: Optional[str] = ""
    # TODO: Not compatible with G2P Connect
    # additional_info: Optional[List[AdditionalInfo]] = []
    additional_info: Optional[AdditionalInfo] = None
    locale: str = "eng"


class LinkCallbackRequest(BaseModel):
    transaction_id: str
    correlation_id: Optional[str] = ""
    link_response: List[SingleLinkCallbackRequest]


class LinkCallbackHttpRequest(BaseModel):
    signature: str
    header: MsgCallbackHeader
    message: LinkCallbackRequest
