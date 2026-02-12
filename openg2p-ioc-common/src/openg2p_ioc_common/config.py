"""Module initializing configs"""

import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from pydantic_settings import BaseSettings, SettingsConfigDict

from .context import config_registry


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="common_", env_file=".env", extra="allow", env_nested_delimiter="__"
    )

    logging_default_logger_name: str = "app"
    logging_level: str = "INFO"
    logging_file_name: Path | None = None

    error_response_debug: bool = False

    keymanager_api_base_url: str = ""
    keymanager_api_timeout: int = 10
    keymanager_api_domain: str = "AUTH"
    keymanager_ssl_verify: bool = False
    keymanager_auth_enabled: bool = True
    keymanager_auth_url: str = ""
    keymanager_auth_client_id: str = "openg2p"
    keymanager_auth_client_secret: str = ""
    keymanager_sign_app_id: str = "OPENG2P"
    keymanager_sign_ref_id: str = ""

    @classmethod
    def get_config(cls, strict=True) -> Self:
        result = None
        cr = config_registry.get()
        if not cr:
            cr = []
            config_registry.set(cr)
        for config in cr:
            if strict:
                if cls is type(config):
                    result = config
                    break
            else:
                if isinstance(config, cls):
                    result = config
                    break
        if not result:
            result = cls()
            cr.append(result)
        return result
