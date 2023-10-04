"""Module containing base models"""

from extendable import ExtendableMeta
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase


class BaseModel(BaseModel, metaclass=ExtendableModelMeta):
    pass


class BaseORMModel(DeclarativeBase, metaclass=ExtendableMeta):
    def update():
        db.update()
