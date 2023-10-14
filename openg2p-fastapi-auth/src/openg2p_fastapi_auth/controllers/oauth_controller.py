import logging
from datetime import datetime, timedelta

import httpx
import orjson
from fastapi import Request
from fastapi.responses import RedirectResponse
from jose import jwt
from openg2p_fastapi_common.controller import BaseController
from openg2p_fastapi_common.errors.http_exceptions import UnauthorizedError

from ..config import Settings
from ..models.orm.login_provider import LoginProvider, LoginProviderTypes
from ..models.provider_auth_parameters import (
    OauthClientAssertionType,
    OauthProviderParameters,
)

_logger = logging.getLogger(__name__)
_config = Settings.get_config(strict=False)


class OAuthController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.router.prefix += "/oauth2"
        self.router.tags += ["oauth"]

        self.router.add_api_route(
            "/callback",
            self.oauth_callback,
            methods=["GET"],
        )

    async def oauth_callback(self, request: Request):
        query_params = request.query_params
        state = orjson.loads(query_params.get("state", "{}"))
        login_provider_id = state.get("p", None)
        if not login_provider_id:
            raise UnauthorizedError("G2P-AUT-401", "Login Provider Id not received")

        login_provider = await LoginProvider.get_by_id(login_provider_id)
        auth_parameters = OauthProviderParameters.model_validate(
            login_provider.authorization_parameters
        )

        if login_provider.type == LoginProviderTypes.oauth2_auth_code:
            token_request_data = {
                "client_id": auth_parameters.client_id,
                "grant_type": "authorization_code",
                "code_verifier": auth_parameters.code_verifier,
                "redirect_uri": auth_parameters.redirect_uri,
                "code": query_params.get("code"),
            }

            token_auth = None
            if (
                auth_parameters.client_assertion_type
                == OauthClientAssertionType.private_key_jwt
            ):
                token_request_data.update(
                    {
                        "client_assertion_type": auth_parameters.client_assertion_type,
                        "client_assertion": jwt.encode(
                            {
                                "iss": auth_parameters.client_id,
                                "sub": auth_parameters.client_id,
                                "aud": auth_parameters.token_endpoint,
                                "exp": datetime.utcnow() + timedelta(hours=1),
                                "iat": datetime.utcnow(),
                            },
                            auth_parameters.client_assertion_jwk,
                            algorithm="RS256",
                        ),
                    }
                )
            elif auth_parameters.client_assertion_type == "client_secret":
                token_auth = (auth_parameters.client_id, auth_parameters.client_secret)
            try:
                res = httpx.post(
                    auth_parameters.token_endpoint,
                    auth=token_auth,
                    data=orjson.loads(orjson.dumps(token_request_data)),
                )
                res.raise_for_status()
                res = res.json()
            except Exception as e:
                _logger.exception(
                    "Error while fetching token from token endpoint, %s",
                    auth_parameters.token_endpoint,
                )
                raise UnauthorizedError(
                    message="Unauthorized. Failed to get token from Oauth Server"
                ) from e

            access_token: str = res["access_token"]
            id_token: str = res["id_token"]

            config_dict = _config.model_dump()
            access_token_payload = jwt.decode(
                access_token,
                None,
                options={
                    "verify_signature": False,
                    "verify_aud": False,
                    "verify_iat": False,
                    "verify_exp": False,
                    "verify_nbf": False,
                    "verify_iss": False,
                    "verify_sub": False,
                    "verify_jti": False,
                },
            )
            response = RedirectResponse(state.get("r", "/"))
            response.set_cookie(
                "X-Access-Token",
                access_token,
                max_age=config_dict.get("auth_cookie_max_age", None),
                expires=access_token_payload.get("exp", None),
                path=config_dict.get("auth_cookie_path", "/"),
                httponly=config_dict.get("auth_cookie_httponly", True),
                secure=config_dict.get("auth_cookie_secure", False),
            )
            response.set_cookie(
                "X-ID-Token",
                id_token,
                max_age=config_dict.get("auth_cookie_max_age", None),
                expires=access_token_payload.get("exp", None),
                path=config_dict.get("auth_cookie_path", "/"),
                httponly=config_dict.get("auth_cookie_httponly", True),
                secure=config_dict.get("auth_cookie_secure", False),
            )

            return response
        else:
            raise NotImplementedError()
