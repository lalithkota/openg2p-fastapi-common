"""Module containing initialization instructions and FastAPI app"""
import logging
import argparse
import sys
from fastapi import FastAPI
from . import config
from .context import app_registry, config_registry
from .component import BaseComponent
import uvicorn
from .config import Settings

_config = config.get_config()

class Initializer(BaseComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initialize()

    def initialize(self):
        """
        Initializes all components
        """
        self.init_config()
        self.init_logger()
        self.init_app()

    def init_config(self) -> Settings:
        config = Settings()
        config_registry.set(config)
        return config

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
        args = self.main_init_args()
        # Check if the 'initialize' flag is provided
        print(args)
        if args.common == 'run':
            # Run your initialization code here
            print("Initializing...")
            self.run_server()
        elif args.common == 'migrate':
            self.migrate_database()
        elif args.common == 'getOpenAPI':
            self.get_openapi()
        else:
            print("Unknown command")

    def main_init_args(self):
        parser = argparse.ArgumentParser(description='FastApi Common Server')
        subparsers = parser.add_subparsers(help='List Commands.', dest='command')
        run_subparser = subparsers.add_parser('run', help='Run API Server.')
        migrate_subparser = subparsers.add_parser('migrate', help='Create/Migrate Database Tables.')
        openapi_subparser = subparsers.add_parser('getOpenAPI', help='Get OpenAPI Json of the Server.')
        openapi_subparser.add_argument('filepath', help='Path of the Output OpenAPI Json File.')
        args = parser.parse_args()
        return args

    def run_server(self):
        app = app_registry.get()
        uvicorn.run(app, host=_config.host, port=_config.port)
        

    def migrate_database(self):
        # Implement the logic for the 'migrate' subcommand here
        print("Running migration...")

    def get_openapi(self):
        # Implement the logic for the 'getOpenAPI' subcommand here
        print("Getting OpenAPI...")


            