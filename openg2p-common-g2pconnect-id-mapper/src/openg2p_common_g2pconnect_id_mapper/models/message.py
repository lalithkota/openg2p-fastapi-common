from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .common import RequestStatusEnum, RequestStatusReasonCode


class MsgHeader(BaseModel):
    version: Optional[str] = "1.0.0"
    message_id: str
    message_ts: datetime
    action: str
    sender_id: str
    sender_uri: Optional[str] = None
    receiver_id: Optional[str] = None
    total_count: int
    is_msg_encrypted: bool = False
    meta: dict = {}


class MsgCallbackHeader(BaseModel):
    version: Optional[str] = "1.0.0"
    message_id: str
    message_ts: datetime
    action: str
    status: RequestStatusEnum
    status_reason_code: Optional[RequestStatusReasonCode] = None
    status_reason_message: Optional[str] = None
    total_count: Optional[int]
    completed_count: Optional[int]
    sender_id: Optional[str]
    receiver_id: Optional[str]
    is_msg_encrypted: bool = False
    meta: dict = {}
