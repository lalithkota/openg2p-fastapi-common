import logging
from typing import Callable, Coroutine, List

from openg2p_fastapi_common.service import BaseService

from ..config import Settings
from ..models.common import MapperValue, TxnStatus
from ..service.link import MapperLinkService
from ..service.resolve import MapperResolveService
from ..service.update import MapperUpdateService

_logger = logging.getLogger(__name__)
_config = Settings.get_config(strict=False)


class MapperUpdateOrLinkService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mapper_update_service = MapperUpdateService.get_component()
        self.mapper_link_service = MapperLinkService.get_component()
        self.mapper_resolve_service = MapperResolveService.get_component()

    async def update_or_link_request(
        self,
        mappings: List[MapperValue],
        callback_func: Callable[[TxnStatus], Coroutine] = None,
    ) -> TxnStatus:
        pass
