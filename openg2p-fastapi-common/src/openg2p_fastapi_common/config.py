"""Module initializing configs"""

from pathlib import Path
from typing import Optional

from extendable_pydantic import ExtendableModelMeta
from pydantic_settings import BaseSettings, SettingsConfigDict

from .context import config_registry


class Settings(BaseSettings, metaclass=ExtendableModelMeta):
    model_config = SettingsConfigDict(env_prefix="common_")

    logging_level: str = "INFO"
    logging_file_name: Optional[Path] = None

    openapi_title: str = "Common"
    openapi_description: str = """
    This is common library for FastAPI service. Override Settings properties to change this.

    ***********************************
    Further details goes here
    ***********************************
    """
    openapi_version: str = "1.0.0"
    openapi_contact_url: str = "https://www.openg2p.org/"
    openapi_contact_email: str = "info@openg2p.org"
    openapi_license_name: str = "Mozilla Public License 2.0"
    openapi_license_url: str = "https://www.mozilla.org/en-US/MPL/2.0/"
    openapi_root_path: Path = "/"

    # TODO:
    db_datasource: Url = ""


def get_config() -> Settings:
    config = config_registry.get()
    return config


def init_config() -> Settings:
    config = Settings()
    config_registry.set(config)
    return config
