from openg2p_fastapi_common.controller import BaseController


class OAuthController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.router.prefix += "/oauth2"
        self.router.tags += ["oauth"]

        self.router.add_api_route(
            "/callback",
            self.oauth_callback,
            # responses={200: {"model": BasicProfile}},
            methods=["GET"],
        )
        self.router.add_api_route(
            "/logout",
            self.oauth_logout,
            # responses={200: {"model": BasicProfile}},
            methods=["GET"],
        )
