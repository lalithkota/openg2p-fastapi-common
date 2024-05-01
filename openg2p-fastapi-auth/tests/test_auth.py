from openg2p_fastapi_auth.app import Initializer as AuthInitializer
from openg2p_fastapi_common.app import Initializer


def test_auth_initializer():
    Initializer()
    AuthInitializer()
