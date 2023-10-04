"""Module from initializing base controllers"""

from typing import Callable

from fastapi import APIRouter
from fastapi.types import DecoratedCallable

from .component import BaseComponent


class BaseController(BaseComponent, APIRouter):
    def __init__(self, name="", **kwargs):
        super(BaseComponent, self).__init__(name)
        super(APIRouter, self).__init__(**kwargs)

    def route(path: str, **kwargs) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            self.add_route(path, func, **kwargs)
            return func

        return decorator

    def api_route(
        path: str, **kwargs
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            self.add_api_route(path, func, **kwargs)
            return func

        return decorator

    def websocket(
        path: str, **kwargs
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            self.add_api_websocket_route(path, func, **kwargs)
            return func

        return decorator

    def websocket_route(
        path: str, **kwargs
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            self.add_websocket_route(path, func, **kwargs)
            return func

        return decorator

    def on_event(event_type: str) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            self.add_event_handler(event_type, func)
            return func

        return decorator

    def get(path: str, **kwargs) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            kwargs["methods"] = ["GET"]
            self.add_api_route(path, func, **kwargs)
            return func

        return decorator

    def put(path: str, **kwargs) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            kwargs["methods"] = ["PUT"]
            self.add_api_route(path, func, **kwargs)
            return func

        return decorator

    def post(path: str, **kwargs) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            kwargs["methods"] = ["POST"]
            self.add_api_route(path, func, **kwargs)
            return func

        return decorator

    def delete(path: str, **kwargs) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            kwargs["methods"] = ["DELETE"]
            self.add_api_route(path, func, **kwargs)
            return func

        return decorator

    def options(
        path: str, **kwargs
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            kwargs["methods"] = ["OPTIONS"]
            self.add_api_route(path, func, **kwargs)
            return func

        return decorator

    def head(path: str, **kwargs) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            kwargs["methods"] = ["HEAD"]
            self.add_api_route(path, func, **kwargs)
            return func

        return decorator

    def patch(path: str, **kwargs) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            kwargs["methods"] = ["PATCH"]
            self.add_api_route(path, func, **kwargs)
            return func

        return decorator

    def trace(path: str, **kwargs) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(self, func: DecoratedCallable) -> DecoratedCallable:
            kwargs["methods"] = ["TRACE"]
            self.add_api_route(path, func, **kwargs)
            return func

        return decorator
