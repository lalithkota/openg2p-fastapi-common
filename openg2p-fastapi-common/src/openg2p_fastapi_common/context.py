"""Module for initializing Contexts"""

from contextvars import ContextVar

from fastapi import FastAPI

app_registry: ContextVar[FastAPI] = ContextVar("app_registry", default=None)
