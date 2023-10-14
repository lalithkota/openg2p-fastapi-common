from typing import List

from pydantic import BaseModel

from .orm.login_provider import LoginProviderTypes


class LoginProviderResponse(BaseModel):
    id: int
    name: str
    type: LoginProviderTypes
    displayName: str
    displayIconUrl: str


class LoginProviderHttpResponse(BaseModel):
    loginProviders: List[LoginProviderResponse]
