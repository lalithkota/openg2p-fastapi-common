from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BasicProfile(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    sub: Optional[str] = None
    iss: Optional[str] = None
    exp: Optional[datetime] = None
    picture: Optional[str] = None
    profile: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[str] = None
    address: Optional[dict] = None
