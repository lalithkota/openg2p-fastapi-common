"""Module containing initialization instructions and FastAPI app"""
import argparse
import logging
import sys

import uvicorn
from fastapi import FastAPI

from .config import Settings
from .context import app_registry

_config = Settings.get_config()


class Initializer:
    def __init__(self):
        self.initialize()

    def initialize(self):
        """
        Initializes all components
        """
        self.init_logger()
        self.init_app()

    def init_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, _config.logging_level))
        logger.addHandler(logging.StreamHandler(sys.stdout))
        if _config.logging_file_name:
            file_handler = logging.FileHandler(_config.logging_file_name)
            logger.addHandler(file_handler)
        return logger

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
            root_path=_config.openapi_root_path if _config.openapi_root_path else "/",
        )
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
            access_log=_config.enable_access_log,
        )

    def migrate_database(self, args):
        # Implement the logic for the 'migrate' subcommand here
        print("Running migration...")

    def get_openapi(self, args):
        # Implement the logic for the 'getOpenAPI' subcommand here
        print(f"Getting OpenAPI... {args.filepath}")
