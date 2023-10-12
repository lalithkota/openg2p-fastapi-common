from openg2p_fastapi_common.config import Settings
from pydantic_settings import SettingsConfigDict


class Settings(Settings):
    model_config = SettingsConfigDict(
        env_prefix="g2pconnect_id_fa_", env_file=".env", extra="allow"
    )

    mapper_resolve_url: str = ""
    mapper_link_url: str = ""
    mapper_update_url: str = ""
    mapper_api_timeout_secs: int = 10

    mapper_common_sender_id: str = "dev.openg2p.net"
    mapper_resolve_sender_url: str = ""
    mapper_link_sender_url: str = ""
    mapper_update_sender_url: str = ""
