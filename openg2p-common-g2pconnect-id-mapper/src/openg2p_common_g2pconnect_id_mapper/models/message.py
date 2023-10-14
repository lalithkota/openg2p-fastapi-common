from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from .common import RequestStatusEnum


class MsgHeaderStatusReasonCodeEnum(Enum):
    rjct_version_invalid = "rjct.version.invalid"
    rjct_message_id_duplicate = "rjct.message_id.duplicate"
    rjct_message_ts_invalid = "rjct.message_ts.invalid"
    rjct_action_invalid = "rjct.action.invalid"
    rjct_action_not_supported = "rjct.action.not_supported"
    rjct_total_count_invalid = "rjct.total_count.invalid"
    rjct_total_count_limit_exceeded = "rjct.total_count.limit_exceeded"
    rjct_errors_too_many = "rjct.errors.too_many"


class MsgHeader(BaseModel):
    version: Optional[str] = "1.0.0"
    message_id: str
    message_ts: datetime
    action: str
    sender_id: str
    sender_uri: Optional[str] = ""
    receiver_id: Optional[str] = ""
    total_count: int
    # TODO: Not compatible with G2P Connect
    # is_msg_encrypted: bool = False
    # meta: dict = {}
    is_encrypted: bool = False


class MsgCallbackHeader(BaseModel):
    version: Optional[str] = "1.0.0"
    message_id: str
    message_ts: datetime
    action: str
    # TODO: Not compatible with G2P Connect
    # status: RequestStatusEnum
    status: Optional[RequestStatusEnum] = None
    status_reason_code: Optional[MsgHeaderStatusReasonCodeEnum] = None
    status_reason_message: Optional[str] = None
    total_count: Optional[int] = -1
    completed_count: Optional[int] = -1
    sender_id: Optional[str] = None
    receiver_id: Optional[str] = None
    # TODO: Not compatible with G2P Connect
    # is_msg_encrypted: bool
    # meta: dict = {}
    is_encrypted: bool
