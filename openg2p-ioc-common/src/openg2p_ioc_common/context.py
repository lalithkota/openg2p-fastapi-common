"""Module for initializing Contexts"""

from contextvars import ContextVar
from typing import TYPE_CHECKING

from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    from .component import BaseComponent

config_registry: ContextVar[list[BaseSettings]] = ContextVar("config_registry", default=None)

component_registry: ContextVar[list["BaseComponent"]] = ContextVar("component_registry", default=None)
