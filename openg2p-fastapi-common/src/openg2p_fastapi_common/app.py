"""Module containing initialization instructions and FastAPI app"""
from fastapi import FastAPI

from . import config, logging
from .context import app_registry

_config = config.get_config()


def init_app():
    app = FastAPI(
        title=_config.openapi_title,
        version=_config.openapi_version,
        description=_config.openapi_description,
        contact={
            "url": _config.openapi_contact_url,
            "email": _config.openapi_contact_email,
        },
        license_info={
            "name": _config.openapi_license_name,
            "url": _config.openapi_license_url,
        },
        root_path=_config.openapi_root_path if _config.openapi_root_path else "/",
    )
    app_registry.set(app)
    return app


def get_app() -> FastAPI:
    app = app_registry.get()
    return app

def init_db():
    _config.db_datasource = "postgresql://localhost:5432/mydb"

def initialize():
    """
    Initializes all components
    """
    config.init_config()
    logging.init_logger()
    init_app()
