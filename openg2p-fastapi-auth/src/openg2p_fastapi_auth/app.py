"""Module initializing auth for APIs"""

import asyncio

from openg2p_fastapi_common.app import Initializer
from openg2p_fastapi_common.config import Settings

from .controllers.auth_controller import AuthController
from .controllers.oauth_controller import OAuthController
from .models.orm.login_provider import LoginProvider

_config = Settings.get_config(strict=False)


class Initializer(Initializer):
    def initialize(self, **kwargs):
        # Initialize all Services, Controllers, any utils here.
        AuthController().post_init()
        OAuthController().post_init()

    def migrate_database(self, args):
        super().migrate_database(args)

        async def migrate():
            await LoginProvider.create_migrate()

        asyncio.run(migrate())
