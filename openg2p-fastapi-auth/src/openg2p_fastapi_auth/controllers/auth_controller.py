import logging
import secrets
import urllib.parse
from typing import Annotated, List, Union

import httpx
import orjson
from fastapi import Depends, Response
from fastapi.responses import RedirectResponse
from jose import jwt
from openg2p_fastapi_common.controller import BaseController
from openg2p_fastapi_common.errors.http_exceptions import InternalServerError

from ..config import Settings
from ..dependencies import JwtBearerAuth
from ..models.credentials import AuthCredentials
from ..models.login_provider import LoginProviderHttpResponse, LoginProviderResponse
from ..models.orm.login_provider import LoginProvider, LoginProviderTypes
from ..models.profile import BasicProfile
from ..models.provider_auth_parameters import OauthProviderParameters

_config = Settings.get_config(strict=False)
_logger = logging.getLogger(__name__)


class AuthController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.router.prefix += "/auth"
        self.router.tags += ["auth"]

        self.router.add_api_route(
            "/profile",
            self.get_profile,
            responses={200: {"model": BasicProfile}},
            methods=["GET"],
        )
        self.router.add_api_route(
            "/logout",
            self.logout,
            methods=["POST"],
        )
        self.router.add_api_route(
            "/getLoginProviders",
            self.get_login_providers,
            responses={200: {"model": LoginProviderHttpResponse}},
            methods=["GET"],
        )
        self.router.add_api_route(
            "/getLoginProviderRedirect/{id}",
            self.get_login_provider_redirect,
            methods=["GET"],
        )

    async def get_profile(
        self,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
        online: bool = True,
    ):
        provider = await LoginProvider.get_login_provider_from_iss(auth.iss)
        if provider.type == LoginProviderTypes.oauth2_auth_code:
            if online:
                return BasicProfile.model_validate(
                    await self.get_oauth_validation_data(
                        auth, iss=auth.iss, provider=provider, combine=True
                    )
                )
            else:
                return BasicProfile.model_validate(auth.model_dump())
        else:
            raise NotImplementedError()

    async def logout(self, response: Response):
        response.delete_cookie("X-Access-Token")
        response.delete_cookie("X-ID-Token")

    async def get_login_providers(self):
        login_providers: List[LoginProvider] = await LoginProvider.get_all()
        return LoginProviderHttpResponse(
            loginProviders=[
                LoginProviderResponse(
                    id=lp.id,
                    name=lp.name,
                    type=lp.type,
                    displayName=lp.login_button_text,
                    displayIconUrl=lp.login_button_image_url,
                )
                for lp in login_providers
            ],
        )

    async def get_login_provider_redirect(self, id: int, redirect_uri: str = "/"):
        login_provider = None
        try:
            login_provider = await LoginProvider.get_by_id(id)
        except Exception:
            _logger.exception("Login Provider fetching: Invalid Id")
            return None
        if login_provider.type == LoginProviderTypes.oauth2_auth_code:
            auth_parameters = OauthProviderParameters.model_validate(
                login_provider.authorization_parameters
            )
            authorize_query_params = {
                "client_id": auth_parameters.client_id,
                "response_type": auth_parameters.response_type,
                "redirect_uri": auth_parameters.redirect_uri,
                "scope": auth_parameters.scope,
                "nonce": secrets.token_urlsafe(),
                "code_verifier": auth_parameters.code_verifier,
                "code_challenge": auth_parameters.code_challenge,
                "code_challenge_method": auth_parameters.code_challenge_method,
                "state": orjson.dumps(
                    {
                        "p": login_provider.id,
                        "r": redirect_uri,
                    }
                ).decode(),
            }

            authorize_query_params.update(auth_parameters.extra_authorize_parameters)
            return RedirectResponse(
                f"{auth_parameters.authorize_endpoint}?{urllib.parse.urlencode(authorize_query_params)}"
            )
        else:
            raise NotImplementedError()

    async def get_oauth_validation_data(
        self,
        auth: Union[str, AuthCredentials],
        id_token: str = None,
        iss: str = None,
        provider: LoginProvider = None,
        combine=True,
    ) -> dict:
        access_token = auth.credentials if isinstance(auth, AuthCredentials) else auth
        if not iss:
            iss = (
                jwt.decode(
                    access_token,
                    None,
                    options={
                        "verify_signature": False,
                        "verify_aud": False,
                        "verify_iss": False,
                        "verify_sub": False,
                    },
                )["iss"]
                if isinstance(auth, str)
                else auth.iss
            )
        if not provider:
            provider = await LoginProvider.get_login_provider_from_iss(iss)
        auth_params = OauthProviderParameters.model_validate(
            provider.authorization_parameters
        )
        try:
            response = httpx.get(
                auth_params.validate_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            if response.headers["content-type"].startswith("application/json"):
                res = response.json()
            if response.headers["content-type"].startswith("application/jwt"):
                res = jwt.decode(
                    res.content,
                    # jwks_cache.get().get(auth.iss),
                    # TODO: Skipping this jwt validation. Some errors.
                    None,
                    options={
                        "verify_signature": False,
                        "verify_aud": False,
                        "verify_nbf": False,
                        "verify_iss": False,
                        "verify_sub": False,
                        "verify_jti": False,
                    },
                )
            if combine:
                return JwtBearerAuth.combine_tokens(access_token, id_token, res)
            else:
                return res
        except Exception as e:
            _logger.exception("Error fetching user profile.")
            raise InternalServerError(
                "G2P-AUT-502",
                f"Error fetching userinfo. {repr(e)}",
            ) from e
