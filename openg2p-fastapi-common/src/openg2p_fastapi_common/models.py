"""Module containing base models"""

from sqlalchemy.orm import DeclarativeBase


class BaseORMModel(DeclarativeBase):
    def __init__(self, **kwargs):
        super(DeclarativeBase, self).__init__(**kwargs)
