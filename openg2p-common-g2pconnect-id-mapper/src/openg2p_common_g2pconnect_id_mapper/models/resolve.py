from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from .common import AccountProviderInfo, AdditionalInfo, RequestStatusEnum
from .message import MsgCallbackHeader, MsgHeader


class ResolveScope(Enum):
    yes_no = "yes_no"
    details = "details"


class ResolveRequestStatusReasonCode(Enum):
    rjct_version_invalid = "rjct.version.invalid"
    rjct_message_id_duplicate = "rjct.message_id.duplicate"
    rjct_message_ts_invalid = "rjct.message_ts.invalid"
    rjct_action_invalid = "rjct.action.invalid"
    rjct_action_not_supported = "rjct.action.not_supported"
    rjct_total_count_invalid = "rjct.total_count.invalid"
    rjct_total_count_limit_exceeded = "rjct.total_count.limit_exceeded"
    rjct_errors_too_many = "rjct.errors.too_many"


class SingleResolveRequest(BaseModel):
    reference_id: str
    timestamp: datetime
    fa: Optional[str]
    id: Optional[str]
    name: Optional[str]
    scope: Optional[ResolveScope] = ResolveScope.details
    additional_info: Optional[List[AdditionalInfo]]
    locale: str = "en"


class ResolveRequest(BaseModel):
    description: Optional[str]
    transaction_id: str
    resolve_request: List[SingleResolveRequest]


class ResolveHttpRequest(BaseModel):
    signature: str
    header: MsgHeader
    message: ResolveRequest


class SingleResolveCallbackRequest(BaseModel):
    reference_id: str
    timestamp: datetime
    fa: Optional[str]
    id: Optional[str]
    account_provider_info: Optional[AccountProviderInfo]
    status: RequestStatusEnum
    status_reason_code: Optional[ResolveRequestStatusReasonCode]
    status_reason_message: Optional[str]
    additional_info: Optional[List[AdditionalInfo]]
    locale: str = "en"


class ResolveCallbackRequest(BaseModel):
    transaction_id: str
    correlation_id: Optional[str]
    resolve_response: List[SingleResolveCallbackRequest]


class ResolveCallbackHttpRequest(BaseModel):
    signature: str
    header: MsgCallbackHeader
    message: ResolveCallbackRequest
