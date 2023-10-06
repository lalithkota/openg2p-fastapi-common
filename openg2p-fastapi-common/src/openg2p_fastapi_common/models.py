"""Module containing base models"""

from sqlalchemy.orm import DeclarativeBase

from .context import dbengine


class BaseORMModel(DeclarativeBase):
    _enabled = True

    def __init__(self, **kwargs):
        super(DeclarativeBase, self).__init__(**kwargs)

    @classmethod
    async def create_migrate(cls):
        if cls._enabled:
            async with dbengine.get().begin() as conn:
                await conn.run_sync(cls.metadata.create_all)
