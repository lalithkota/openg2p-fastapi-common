from contextvars import ContextVar
from typing import Any, Dict

jwks_cache: ContextVar[Dict[str, Any]] = ContextVar("jwks_cache", default=[])
