from contextvars import ContextVar
from typing import Any, Dict

# TODO: Handle JWKs Cache properly
jwks_cache: ContextVar[Dict[str, Any]] = ContextVar("jwks_cache", default={})
