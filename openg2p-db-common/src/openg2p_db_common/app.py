"""Module containing initialization instructions and FastAPI app"""

import logging

from sqlalchemy.ext.asyncio import create_async_engine

from openg2p_ioc_common.app import Initializer as BaseInitializer

from .config import Settings
from .context import dbengine

_config = Settings.get_config(strict=False)
_logger = logging.getLogger(_config.logging_default_logger_name)


class Initializer(BaseInitializer):
    def init_db(self):
        if _config.db_datasource:
            db_engine = create_async_engine(_config.db_datasource, echo=_config.db_logging)
            dbengine.set(db_engine)

    def main_create_parser(self):
        parser, sp = super().main_create_parser()
        migrate_subparser = sp.add_parser("migrate", help="Create/Migrate Database Tables.")
        migrate_subparser.set_defaults(func=self.migrate_database)
        return parser, sp

    def migrate_database(self, args):
        # Implement the logic for the 'migrate' subcommand here
        _logger.info("Starting DB migrations.")
