"""Module from initializing base controllers"""

from fastapi.datastructures import Default
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute, APIRouter

from .component import BaseComponent
from .config import Settings
from .context import app_registry
from .errors import ErrorListResponse

_config = Settings.get_config(strict=False)


class BaseController(BaseComponent):
    def __init__(self, name="", **kwargs):
        super().__init__(name=name)
        if "default_response_class" not in kwargs:
            kwargs["default_response_class"] = Default(ORJSONResponse)
        self.router = APIRouter(**kwargs)
        if _config.openapi_common_api_prefix:
            self.router.prefix = _config.openapi_common_api_prefix

    def post_init(self):
        for route in self.router.routes:
            if isinstance(route, APIRoute):
                # Add default responses to APIs. Original Responses take preference.
                default_responses = {
                    401: {"model": ErrorListResponse},
                    403: {"model": ErrorListResponse},
                    404: {"model": ErrorListResponse},
                    500: {"model": ErrorListResponse},
                }
                default_responses.update(route.responses)
                route.responses = default_responses
        app_registry.get().include_router(self.router)
        return self
