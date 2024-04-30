from openg2p_fastapi_common.app import Initializer
from openg2p_fastapi_auth.app import Initializer as AuthInitializer

def test_auth_initializer():
    Initializer()
    AuthInitializer()
