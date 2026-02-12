"""Module containing initialization instructions and FastAPI app"""

import logging
from contextlib import asynccontextmanager

import json_logging
import orjson
import uvicorn
from fastapi import FastAPI

from openg2p_ioc_common.app import Initializer as BaseInitializer
from openg2p_ioc_common.service import BaseAsyncService
from openg2p_ioc_common.context import component_registry

from .config import Settings, WorkerType
from .context import app_registry
from .exception import BaseExceptionHandler

_config = Settings.get_config(strict=False)
_logger = logging.getLogger(_config.logging_default_logger_name)


class Initializer(BaseInitializer):
    def init_logger(self):
        logger = super().init_logger()
        json_logging.init_fastapi(enable_json=True)
        json_logging.JSON_SERIALIZER = lambda log: orjson.dumps(log).decode("utf-8")
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
            lifespan=self.fastapi_app_lifespan,
            root_path=_config.openapi_root_path if _config.openapi_root_path else "",
        )
        json_logging.init_request_instrument(app)
        app_registry.set(app)
        self.create_exception_handler()
        _logger.info(
            "Worker ID - %s. Docker Pod ID - %s",
            _config.worker_id,
            _config.docker_pod_id,
        )
        return app
    
    def create_exception_handler(self):
        return BaseExceptionHandler(app=app_registry.get())

    def return_app(self):
        return app_registry.get()

    def main_create_parser(self):
        parser, sp = super().main_create_parser()
        run_subparser = sp.add_parser("run", help="Run API Server.")
        run_subparser.set_defaults(func=self.run_server)
        openapi_subparser = sp.add_parser("getOpenAPI", help="Get OpenAPI Json of the Server.")
        openapi_subparser.add_argument("filepath", help="Path of the Output OpenAPI Json File.")
        openapi_subparser.set_defaults(func=self.get_openapi)
        return parser, sp

    def run_server(self, args):
        app = self.return_app()
        if _config.worker_type == WorkerType.gunicorn:
            import subprocess

            subprocess.run(
                f'gunicorn "main:app" --workers {_config.no_of_workers} --worker-class uvicorn.workers.UvicornWorker --bind {_config.host}:{_config.port}',
                shell=True,
            )
        if _config.worker_type == WorkerType.uvicorn:
            import subprocess

            subprocess.run(
                f'uvicorn "main:app" --workers {_config.no_of_workers} --host {_config.host} --port {_config.port}',
                shell=True,
            )
        if _config.worker_type == WorkerType.local:
            uvicorn.run(
                app,
                host=_config.host,
                port=_config.port,
                access_log=False,
                # The following is not possible
                # workers=_config.no_of_workers
            )

    def get_openapi(self, args):
        app = self.return_app()
        with open(args.filepath, "wb+") as f:
            f.write(orjson.dumps(app.openapi(), option=orjson.OPT_INDENT_2))
            f.write(b"\n")

    async def fastapi_app_startup(self, app: FastAPI):
        # Overload this method to execute something on startup
        pass

    async def fastapi_app_shutdown(self, app: FastAPI):
        # Overload this method to execute something on shutdown
        try:
            from openg2p_db_common.context import dbengine

            if dbengine.get():
                await dbengine.get().dispose()
                dbengine.set(None)
        except ImportError:
            pass

    @asynccontextmanager
    async def fastapi_app_lifespan(self, app: FastAPI):
        cr = component_registry.get() or []
        for component in cr:
            if isinstance(component, Initializer):
                await component.fastapi_app_startup(app)
        yield
        for component in cr:
            if isinstance(component, Initializer):
                await component.fastapi_app_shutdown(app)
            elif isinstance(component, BaseAsyncService):
                await component.aclose()
