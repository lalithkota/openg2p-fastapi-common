"""Module containing base models"""

from sqlalchemy.orm import DeclarativeBase

from .component import BaseComponent


class BaseORMModel(BaseComponent, DeclarativeBase):
    def __init__(self, name="", **kwargs):
        super(BaseComponent, self).__init__(name)
        super(DeclarativeBase, self).__init__(**kwargs)
