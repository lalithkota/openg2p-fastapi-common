"""Module initializing configs"""

from pathlib import Path
from typing import Optional

from extendable_pydantic import ExtendableModelMeta
from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from .context import config_registry


class Settings(BaseSettings, metaclass=ExtendableModelMeta):
    model_config = SettingsConfigDict(env_prefix="common_")

    host: str = "localhost"
    port: int = 8000

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

    # If empty will be constructed like this
    # f"{db_driver}://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_dbname}"
    db_datasource: Optional[AnyUrl]
    db_driver: str = "postgresql+asyncpg"
    db_username: Optional[str]
    db_password: Optional[str]
    db_hostname: str = "localhost"
    db_port: int = 5432
    db_dbname: Optional[str]


def get_config() -> Settings:
    config = config_registry.get()
    return config
