from datetime import datetime
from typing import Optional, Union

from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ConfigDict


class AuthCredentials(HTTPAuthorizationCredentials):
    model_config = ConfigDict(extra="allow")

    scheme: str = "bearer"
    credentials: str
    iss: str = None
    sub: str = None
    aud: Optional[Union[str, list]] = None
    iat: Optional[datetime] = None
    exp: Optional[datetime] = None
