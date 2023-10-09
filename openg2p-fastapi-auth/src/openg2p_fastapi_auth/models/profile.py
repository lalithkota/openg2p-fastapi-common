from typing import Optional

from pydantic import BaseModel


class BasicProfile(BaseModel):
    name: Optional[str] = None
    sub: Optional[str] = None
    iss: Optional[str] = None
    picture: Optional[str] = None
    profile: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[str] = None
    address: Optional[dict] = None
