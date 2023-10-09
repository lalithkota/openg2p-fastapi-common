from openg2p_fastapi_common.controller import BaseController

from ..models.profile import BasicProfile


class AuthController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.router.prefix += "/auth"
        self.router.tags += ["auth"]

        self.router.add_api_route(
            "/profile",
            self.get_profile,
            responses={200: {"model": BasicProfile}},
            methods=["GET"],
        )
        self.router.add_api_route(
            "/getLoginProviders",
            self.get_login_providers,
            responses={200: {"model": BasicProfile}},
            methods=["GET"],
        )

    async def get_profile(self, _online: bool = False):
        pass
