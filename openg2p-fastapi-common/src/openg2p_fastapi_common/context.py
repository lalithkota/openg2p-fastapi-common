"""Module for initializing Contexts"""

from contextvars import ContextVar
from typing import List, Optional

from extendable import registry, ExtendableMeta
from extendable.context import extendable_registry


from fastapi import FastAPI
from pydantic_settings import BaseSettings


_registry = registry.ExtendableClassesRegistry()
extendable_registry.set(_registry)
_registry.init_registry()

app_registry: ContextVar[Optional[FastAPI]] = ContextVar("app_registry", default=None)

config_registry: ContextVar[Optional[BaseSettings]] = ContextVar(
    "config_registry", default=None
)

class _Component(metaclass=ExtendableMeta):
    def __init__(self, name=""):
        self.name = name

    def __repr__(self) -> str:
        return self.name

print(extendable_registry.get()._extendable_classes)

component_registry: ContextVar[List[_Component]] = ContextVar(
    "component_registry", default=[]
)

