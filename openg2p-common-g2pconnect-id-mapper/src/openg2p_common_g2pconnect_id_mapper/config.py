from openg2p_fastapi_common.config import Settings
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
