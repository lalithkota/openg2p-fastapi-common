from datetime import datetime
from typing import Optional

from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ConfigDict


class AuthCredentials(HTTPAuthorizationCredentials):
    model_config = ConfigDict(extra="allow")

    scheme: str = "bearer"
    provider_id: Optional[int] = None
    credentials: str
    iss: str = None
    sub: str = None
    aud: Optional[str] = None
    iat: Optional[datetime] = None
    exp: Optional[datetime] = None
