"""Module containing initialization IOC app"""

import argparse
import logging
import sys

from .component import BaseComponent
from .config import Settings

_config = Settings.get_config(strict=False)
_logger = logging.getLogger(_config.logging_default_logger_name)


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

    def init_logger(self):
        _logger.setLevel(getattr(logging, _config.logging_level))
        _logger.addHandler(logging.StreamHandler(sys.stdout))
        if _config.logging_file_name:
            file_handler = logging.FileHandler(_config.logging_file_name)
            _logger.addHandler(file_handler)
        return _logger

    def init_db(self):
        """To be implemented by submodule"""

    def init_app(self):
        """To be implemented by submodule"""

    def return_app(self):
        """To be implemented by submodule"""
        raise NotImplementedError()
    
    def main_create_parser(self):
        parser = argparse.ArgumentParser(description="Common Service")
        sp = parser.add_subparsers(dest="command", help="List Commands.", required=True)
        return parser, sp

    def main(self):
        parser, _ = self.main_create_parser()
        args = parser.parse_args()
        args.func(args)
