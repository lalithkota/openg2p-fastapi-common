from typing import Optional

from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ConfigDict


class AuthCredentials(HTTPAuthorizationCredentials):
    model_config = ConfigDict(extra="allow")

    scheme: str = "bearer"
    credentials: str
    iss: str = None
    sub: str = None
    aud: Optional[str] = None
