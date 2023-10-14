# ruff: noqa: E402

from .config import Settings

_config = Settings.get_config(strict=False)

from .app import Initializer
from .controller import BaseController


class PingController(BaseController):
    def __init__(self, name="", **kwargs):
        super().__init__(name, **kwargs)

        self.router.prefix += "/ping"
        self.router.tags += ["ping"]

        self.router.add_api_route(
            "/",
            self.get_ping,
            methods=["GET"],
        )

    async def get_ping(self):
        return "pong"


class PingInitializer(Initializer):
    def initialize(self, **kwargs):
        # Initialize all Services, Controllers, any utils here.
        PingController().post_init()
