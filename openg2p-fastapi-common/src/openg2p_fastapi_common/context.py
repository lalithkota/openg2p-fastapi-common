"""Module for initializing Contexts"""

from contextvars import ContextVar
from typing import List, Optional

from fastapi import FastAPI
from pydantic_settings import BaseSettings

app_registry: ContextVar[Optional[FastAPI]] = ContextVar("app_registry", default=None)

config_registry: ContextVar[Optional[BaseSettings]] = ContextVar(
    "config_registry", default=None
)

# The following is a list of BaseComponents
component_registry: ContextVar[List] = ContextVar("component_registry", default=[])
