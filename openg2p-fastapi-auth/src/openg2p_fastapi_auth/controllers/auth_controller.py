import logging
import secrets
import urllib.parse
from typing import Annotated, List

import httpx
import orjson
from fastapi import Depends
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
        # TODO: Handle updating response with auth
        if provider.type == LoginProviderTypes.oauth2_auth_code:
            if online:
                auth_params = OauthProviderParameters.model_validate(
                    provider.authorization_parameters
                )
                try:
                    res = httpx.get(
                        auth_params.validate_endpoint,
                        headers={"Authorization": f"Bearer {auth.credentials}"},
                    )
                    res.raise_for_status()
                    if res.headers["content-type"].startswith("application/json"):
                        return BasicProfile.model_validate(res.json())
                    if res.headers["content-type"].startswith("application/jwt"):
                        return BasicProfile.model_validate(
                            jwt.decode(
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
                        )
                except Exception as e:
                    _logger.exception("Error fetching user profile.")
                    raise InternalServerError(
                        "G2P-AUT-502",
                        f"Error fetching userinfo. {repr(e)}",
                    ) from e
            return BasicProfile(**auth.model_dump())
        else:
            raise NotImplementedError()

    async def logout(
        self,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ):
        config_dict = _config.model_dump()
        response = RedirectResponse(config_dict.get("auth_logout_url", "/"))
        response.set_cookie(
            "X-Access-Token",
            None,
            max_age=-1,
            path=config_dict.get("auth_cookie_path", "/"),
            httponly=config_dict.get("auth_cookie_httponly", True),
            secure=config_dict.get("auth_cookie_secure", False),
        )
        response.set_cookie(
            "X-ID-Token",
            None,
            max_age=-1,
            path=config_dict.get("auth_cookie_path", "/"),
            httponly=config_dict.get("auth_cookie_httponly", True),
            secure=config_dict.get("auth_cookie_secure", False),
        )
        return response

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
