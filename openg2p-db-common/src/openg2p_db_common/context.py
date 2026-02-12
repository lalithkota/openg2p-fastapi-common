"""Module for initializing Contexts"""

from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncEngine

dbengine: ContextVar[AsyncEngine] = ContextVar("dbengine", default=None)
