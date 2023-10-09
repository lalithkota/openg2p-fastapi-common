"""Module initializing auth for APIs"""

from openg2p_fastapi_common.app import Initializer
from openg2p_fastapi_common.config import Settings

from .auth_middleware import JwtAuthenticationMiddleware

_config = Settings.get_config(strict=False)


class Initializer(Initializer):
    def initialize(self, **kwargs):
        # Initialize all Services, Controllers, any utils here.
        JwtAuthenticationMiddleware()
