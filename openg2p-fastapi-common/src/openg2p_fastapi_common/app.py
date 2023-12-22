"""Module containing initialization instructions and FastAPI app"""
import argparse
import logging
import sys
from contextlib import asynccontextmanager

import json_logging
import orjson
import uvicorn
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from .component import BaseComponent
from .config import Settings
from .context import app_registry, component_registry, dbengine
from .exception import BaseExceptionHandler

_config = Settings.get_config(strict=False)
_logger = logging.getLogger(__name__)


class Initializer(BaseComponent):
    def __init__(self, name="", **kwargs):
        super().__init__(name=name, **kwargs)
        self.initialize()

    def initialize(self):
        """
        Initializes all components
        """
        self.init_logger()
        self.init_app()
        self.init_db()

        BaseExceptionHandler()

    def init_logger(self):
        json_logging.init_fastapi(enable_json=True)
        json_logging.JSON_SERIALIZER = lambda log: orjson.dumps(log).decode("utf-8")
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, _config.logging_level))
        logger.addHandler(logging.StreamHandler(sys.stdout))
        if _config.logging_file_name:
            file_handler = logging.FileHandler(_config.logging_file_name)
            logger.addHandler(file_handler)
        return logger

    def init_db(self):
        if _config.db_datasource:
            db_engine = create_async_engine(
                _config.db_datasource, echo=_config.db_logging
            )
            dbengine.set(db_engine)

    def init_app(self):
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
            lifespan=self.fastapi_app_lifespan,
            root_path=_config.openapi_root_path if _config.openapi_root_path else "",
        )
        json_logging.init_request_instrument(app)
        app_registry.set(app)
        return app

    def main(self):
        parser = argparse.ArgumentParser(description="FastApi Common Server")
        subparsers = parser.add_subparsers(help="List Commands.", required=True)
        run_subparser = subparsers.add_parser("run", help="Run API Server.")
        run_subparser.set_defaults(func=self.run_server)
        migrate_subparser = subparsers.add_parser(
            "migrate", help="Create/Migrate Database Tables."
        )
        migrate_subparser.set_defaults(func=self.migrate_database)
        openapi_subparser = subparsers.add_parser(
            "getOpenAPI", help="Get OpenAPI Json of the Server."
        )
        openapi_subparser.add_argument(
            "filepath", help="Path of the Output OpenAPI Json File."
        )
        openapi_subparser.set_defaults(func=self.get_openapi)
        args = parser.parse_args()
        args.func(args)

    def run_server(self, args):
        app = app_registry.get()
        uvicorn.run(
            app,
            host=_config.host,
            port=_config.port,
            access_log=False,
        )

    def migrate_database(self, args):
        # Implement the logic for the 'migrate' subcommand here
        _logger.info("Starting DB migrations.")

    def get_openapi(self, args):
        app = app_registry.get()
        with open(args.filepath, "wb+") as f:
            f.write(orjson.dumps(app.openapi(), option=orjson.OPT_INDENT_2))
            f.write(b"\n")

    async def fastapi_app_startup(self, app: FastAPI):
        # Overload this method to execute something on startup
        pass

    async def fastapi_app_shutdown(self, app: FastAPI):
        # Overload this method to execute something on shutdown
        if dbengine.get():
            await dbengine.get().dispose()
            dbengine.set(None)

    @asynccontextmanager
    async def fastapi_app_lifespan(self, app: FastAPI):
        for initializer in component_registry.get():
            if isinstance(initializer, Initializer):
                await initializer.fastapi_app_startup(app)
        yield
        for initializer in component_registry.get():
            if isinstance(initializer, Initializer):
                await initializer.fastapi_app_shutdown(app)
