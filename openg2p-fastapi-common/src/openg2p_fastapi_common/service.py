"""Module for initiailizing base Service"""

from .component import BaseComponent


class BaseService(BaseComponent):
    def __init__(self, name=""):
        super().__init__(name)
