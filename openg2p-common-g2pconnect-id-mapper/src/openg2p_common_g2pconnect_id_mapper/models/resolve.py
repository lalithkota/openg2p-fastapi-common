from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from .common import (
    AccountProviderInfo,
    RequestStatusEnum,
    SingleCommonRequest,
)
from .message import MsgCallbackHeader, MsgHeader


class ResolveScope(Enum):
    yes_no = "yes_no"
    details = "details"


class ResolveRequestStatusReasonCode(Enum):
    rjct_reference_id_invalid = "rjct.reference_id.invalid"
    rjct_reference_id_duplicate = "rjct.reference_id.duplicate"
    rjct_timestamp_invalid = "rjct.timestamp.invalid"
    rjct_id_invalid = "rjct.id.invalid"
    rjct_fa_invalid = "rjct.fa.invalid"
    rjct_resolve_type_not_supported = "rjct.resolve_type.not_supported"
    succ_fa_active = "succ.fa.active"
    succ_fa_inactive = "succ.fa.inactive"
    succ_fa_not_found = "succ.fa.not_found"
    succ_fa_not_linked_to_id = "succ.fa.not_linked_to_id"
    succ_id_active = "succ.id.active"
    succ_id_inactive = "succ.id.inactive"
    succ_id_not_found = "succ.id.not_found"


class SingleResolveRequest(SingleCommonRequest):
    fa: Optional[str] = ""
    id: Optional[str] = ""
    name: Optional[str] = None
    scope: Optional[ResolveScope] = ResolveScope.details


class ResolveRequest(BaseModel):
    transaction_id: str
    resolve_request: List[SingleResolveRequest]


class ResolveHttpRequest(BaseModel):
    signature: str
    header: MsgHeader
    message: ResolveRequest


class SingleResolveCallbackRequest(SingleCommonRequest):
    fa: Optional[str] = None
    id: Optional[str] = None
    account_provider_info: Optional[AccountProviderInfo] = None
    status: RequestStatusEnum
    status_reason_code: Optional[ResolveRequestStatusReasonCode] = None
    status_reason_message: Optional[str] = ""


class ResolveCallbackRequest(BaseModel):
    transaction_id: str
    correlation_id: Optional[str] = ""
    resolve_response: List[SingleResolveCallbackRequest]


class ResolveCallbackHttpRequest(BaseModel):
    signature: str
    header: MsgCallbackHeader
    message: ResolveCallbackRequest
