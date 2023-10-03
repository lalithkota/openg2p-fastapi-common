"""Module from initializing base controllers"""

from fastapi import APIRouter

from .component import BaseComponent


class BaseController(BaseComponent, APIRouter):
    # post = APIRouter.post
    # get = APIRouter.get
    # patch = APIRouter.patch
    # put = APIRouter.put
    # delete = APIRouter.delete
    # options = APIRouter.options
    # trace = APIRouter.trace
    # api_route = APIRouter.api_route

    def __init__(self, name="", **kwargs):
        super(BaseComponent, self).__init__(name)
        super(APIRouter, self).__init__(**kwargs)
