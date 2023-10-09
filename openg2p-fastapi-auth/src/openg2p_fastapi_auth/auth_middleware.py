import httpx
from fastapi import Request
from jose import jwt
from openg2p_fastapi_common.component import BaseComponent
from openg2p_fastapi_common.config import Settings
from openg2p_fastapi_common.context import app_registry
from openg2p_fastapi_common.errors.http_exceptions import (
    ForbiddenError,
    UnauthorizedError,
)
from starlette.middleware.base import BaseHTTPMiddleware

from .context import jwks_cache

_config = Settings.get_config(strict=False)


class JwtAuthenticationMiddleware(BaseComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app_registry.get().add_middleware(
            BaseHTTPMiddleware, dispatch=self.perform_jwt_auth
        )

    async def perform_jwt_auth(self, request: Request, call_next):
        config_dict = _config.model_dump()
        if not config_dict.get("auth_enabled", None):
            return await call_next()

        api_call_name = str(request.scope["route"].name)

        api_auth_settings = config_dict.get("auth_api_" + api_call_name, None)

        if (not api_auth_settings) or (not api_auth_settings.get("enabled", None)):
            return await call_next()

        issuers_list = api_auth_settings.get("issuers", None) or config_dict.get(
            "auth_default_issuers", []
        )
        audiences_list = api_auth_settings.get("audiences", None) or config_dict.get(
            "auth_default_audiences", []
        )
        jwks_urls_list = api_auth_settings.get("jwks_urls", None) or config_dict.get(
            "auth_default_jwks_urls", []
        )

        jwt_token = (
            request.headers["Authorization"] or request.cookies["X-Access-Token"]
        )
        if jwt_token:
            jwt_token = jwt_token.removeprefix("Bearer ")

        if not jwt_token:
            raise UnauthorizedError()

        unverified_payload = jwt.decode(
            jwt_token, None, options={"verify_signature": False}
        )
        iss = unverified_payload["iss"]
        aud = unverified_payload.get("aud", None)
        if iss not in issuers_list:
            raise UnauthorizedError(message="Unauthorized. Unknown Issuer.")

        if audiences_list:
            if not (aud and aud in audiences_list):
                raise UnauthorizedError(message="Unauthorized. Unknown Audience.")

        jwks = jwks_cache.get().get(iss, None)

        if not jwks:
            jwks_list_index = list(issuers_list).index(iss)
            jwks_url = (
                jwks_urls_list[jwks_list_index]
                if jwks_list_index < len(jwks_urls_list)
                else iss.rstrip("/") + "/.well-known/jwks.json"
            )
            try:
                res = httpx.get(jwks_url)
                res.raise_for_status()
                jwks = res.json()
                jwks_cache.get().update(iss, jwks)
            except Exception as e:
                raise UnauthorizedError(
                    message=f"Unauthorized. Could not fetch Jwks. {repr(e)}"
                ) from e

        try:
            jwt.decode(jwt_token, jwks)
        except Exception as e:
            raise UnauthorizedError(
                message=f"Unauthorized. Invalid Jwt. {repr(e)}"
            ) from e

        claim_to_check = config_dict.get("claim_name", None)
        claim_values = config_dict.get("claim_values", None)
        if claim_to_check:
            claims = unverified_payload.get(claim_to_check, None)
            if not claims:
                raise ForbiddenError(message="Forbidden. Claim(s) missing.")
            if isinstance(claims, str):
                if len(claim_values) != 1 or claim_values[0] != claims:
                    raise ForbiddenError(message="Forbidden. Claim doesn't match.")
            else:
                if all(x in claims for x in claim_values):
                    raise ForbiddenError(message="Forbidden. Claim(s) don't match.")

        request.auth = unverified_payload

        return await call_next(request)
