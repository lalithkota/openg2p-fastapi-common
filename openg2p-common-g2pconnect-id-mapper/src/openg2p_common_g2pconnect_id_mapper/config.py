from typing import Optional

from openg2p_fastapi_common.config import Settings
from pydantic import model_validator
from pydantic_settings import SettingsConfigDict


class Settings(Settings):
    model_config = SettingsConfigDict(
        env_prefix="g2pconnect_id_fa_", env_file=".env", extra="allow"
    )
    callback_api_common_prefix: str = "/callback"

    mapper_resolve_url: str = "http://localhost:8766/v0.1.0/mapper/resolve"
    mapper_link_url: str = "http://localhost:8766/v0.1.0/mapper/link"
    mapper_update_url: str = "http://localhost:8766/v0.1.0/mapper/update"
    mapper_api_timeout_secs: int = 10

    mapper_common_sender_id: str = "dev.openg2p.net"
    mapper_resolve_sender_url: str = "http://localhost:8000/callback/mapper"
    mapper_link_sender_url: str = "http://localhost:8000/callback/mapper"
    mapper_update_sender_url: str = "http://localhost:8000/callback/mapper"

    queue_redis_source: Optional[str] = None
    queue_redis_username: Optional[str] = None
    queue_redis_password: Optional[str] = None
    queue_redis_host: Optional[str] = "localhost"
    queue_redis_port: Optional[int] = 6379
    queue_redis_dbindex: Optional[int] = 0

    queue_link_name: str = "mapper-link:"
    queue_resolve_name: str = "mapper-resolve:"
    queue_update_name: str = "mapper-update:"

    @model_validator(mode="after")
    def validate_queue_redis_source(self) -> "Settings":
        if self.queue_redis_source:
            return self
        source = "redis://"
        if self.queue_redis_username:
            source += f"{self.queue_redis_username}:{self.queue_redis_password}@"
        if self.queue_redis_host:
            source += f"{self.queue_redis_host}:{self.db_port}"
        if self.queue_redis_dbindex:
            source += f"/{self.queue_redis_dbindex}"

        self.queue_redis_source = source

        return self
