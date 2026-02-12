"""Module initializing configs"""

from pydantic import model_validator
from pydantic_settings import SettingsConfigDict

from openg2p_ioc_common.config import Settings as BaseSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="common_", env_file=".env", extra="allow", env_nested_delimiter="__"
    )

    # If empty will be constructed like this
    # f"{db_driver}://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_dbname}"
    db_datasource: str = ""
    db_driver: str = "postgresql+asyncpg"
    db_username: str = ""
    db_password: str = ""
    db_hostname: str = "localhost"
    db_port: int = 5432
    db_dbname: str = ""
    db_logging: bool = False

    @model_validator(mode="after")
    def validate_db_datasource(self):
        if self.db_datasource:
            return self
        datasource = ""
        if self.db_driver:
            datasource += f"{self.db_driver}://"
        if self.db_username:
            datasource += f"{self.db_username}:{self.db_password}@"
        if self.db_hostname:
            datasource += self.db_hostname
        if self.db_port:
            datasource += f":{self.db_port}"
        if self.db_dbname:
            datasource += f"/{self.db_dbname}"

        self.db_datasource = datasource

        return self
