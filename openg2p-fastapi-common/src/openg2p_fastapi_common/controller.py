"""Module from initializing base controllers"""

from fastapi.datastructures import Default
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter

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
        self.router.responses = {
            401: {"model": ErrorListResponse},
            403: {"model": ErrorListResponse},
            404: {"model": ErrorListResponse},
            500: {"model": ErrorListResponse},
        }
        if _config.openapi_common_api_prefix:
            self.router.prefix = _config.openapi_common_api_prefix

    def post_init(self):
        app_registry.get().include_router(self.router)
        return self
