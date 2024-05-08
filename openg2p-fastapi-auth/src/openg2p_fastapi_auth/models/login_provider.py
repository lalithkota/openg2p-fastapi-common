from typing import List, Union

from pydantic import BaseModel

from .orm.login_provider import LoginProviderTypes


class LoginProviderResponse(BaseModel):
    id: int
    name: str
    type: LoginProviderTypes
    displayName: Union[str, dict]
    displayIconUrl: str


class LoginProviderHttpResponse(BaseModel):
    loginProviders: List[LoginProviderResponse]
