"""Module containing base models"""

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel
from .component import BaseComponent
from sqlalchemy.orm import DeclarativeBase


class BaseModel(BaseModel, metaclass=ExtendableModelMeta):
    pass


class BaseORMModel(BaseComponent, DeclarativeBase):

    def __init__(self, name="", **kwargs):
        super(BaseComponent, self).__init__(name)
        super(DeclarativeBase, self).__init__(**kwargs)
    
