"""Module initializing configs"""

import os
from enum import Enum

from pydantic import model_validator
from pydantic_settings import SettingsConfigDict

from openg2p_ioc_common.config import Settings as BaseSettings

from . import __version__


class WorkerType(Enum):
    local = "local"
    uvicorn = "uvicorn"
    gunicorn = "gunicorn"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="common_", env_file=".env", extra="allow", env_nested_delimiter="__"
    )

    host: str = "0.0.0.0"
    port: int = 8000

    no_of_workers: int = 1
    worker_id: int = -1
    worker_pid: int = -1
    worker_type: WorkerType = WorkerType.local
    docker_pod_id: str = ""
    docker_pod_name: str = ""

    openapi_title: str = "Common"
    openapi_description: str = """
    This is common library for FastAPI service. Override Settings properties to change this.

    ***********************************
    Further details goes here
    ***********************************
    """
    openapi_version: str = __version__
    openapi_contact_url: str = "https://www.openg2p.org/"
    openapi_contact_email: str = "info@openg2p.org"
    openapi_license_name: str = "Mozilla Public License 2.0"
    openapi_license_url: str = "https://www.mozilla.org/en-US/MPL/2.0/"
    openapi_root_path: str = ""
    openapi_common_api_prefix: str = ""

    @model_validator(mode="after")
    def validate_worker_ids_and_pod_ids(self):
        self.set_current_worker_id()
        self.set_current_docker_pod_id()
        return self

    def set_current_worker_id(self):
        if self.worker_type == WorkerType.local:
            return
        try:
            self.worker_pid = os.getpid()
            import subprocess

            pid_arr = sorted(
                [
                    int(a)
                    for a in str(
                        subprocess.check_output(["pgrep", "-f", self.worker_type.value]),
                        "UTF-8",
                    ).split("\n")
                    if a
                ]
            )
            self.worker_id = pid_arr.index(self.worker_pid) - 1
        except Exception:
            pass

    def set_current_docker_pod_id(self):
        self.docker_pod_id = str(self.docker_pod_name.split("-")[-1])
