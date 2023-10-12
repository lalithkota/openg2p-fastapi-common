# ruff: noqa: E402

from .config import Settings

_config = Settings.get_config(strict=False)

from openg2p_fastapi_common.app import Initializer

from .controllers.link_callback import LinkCallbackController
from .controllers.resolve_callback import ResolveCallbackController
from .controllers.update_callback import UpdateCallbackController
from .service.link import MapperLinkService
from .service.resolve import MapperResolveService
from .service.update import MapperUpdateService
from .service.update_link import MapperUpdateOrLinkService


class Initializer(Initializer):
    def initialize(self, **kwargs):
        # Initialize all Services, Controllers, any utils here.
        MapperResolveService()
        MapperLinkService()
        MapperUpdateService()
        MapperUpdateOrLinkService()

        LinkCallbackController().post_init()
        UpdateCallbackController().post_init()
        ResolveCallbackController().post_init()
