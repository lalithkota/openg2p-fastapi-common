"""Module for initializing Contexts"""

from contextvars import ContextVar
from typing import List, Optional

from extendable import registry
from extendable.context import extendable_registry
from fastapi import FastAPI
from pydantic_settings import BaseSettings

from .component import BaseComponent

_registry = registry.ExtendableClassesRegistry()
extendable_registry.set(_registry)
_registry.init_registry()

app_registry: ContextVar[Optional[FastAPI]] = ContextVar("app_registry", default=None)

config_registry: ContextVar[Optional[BaseSettings]] = ContextVar(
    "config_registry", default=None
)

component_registry: ContextVar[List[BaseComponent]] = ContextVar(
    "component_registry", default=[]
)
