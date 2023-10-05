"""Module from initializing base controllers"""

from fastapi import APIRouter

from .component import BaseComponent
from .context import app_registry


class BaseController(BaseComponent):
    def __init__(self, name="", **kwargs):
        super().__init__(name=name)
        self.router = APIRouter(**kwargs)

    def post_init(self):
        app_registry.get().include_router(self.router)
        return self
