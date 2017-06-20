import logging
import os

import sys

import colorama
from colorlog import colorlog

if 'PYCHARM_HOSTED' in os.environ:
    colorama.deinit()


class LogHelper:
    FORMATTER_COLOR = colorlog.ColoredFormatter('{log_color}{asctime} {name}: {levelname:<8s} {message}', style='{')
    FORMATTER = logging.Formatter('{asctime} {name}: {levelname:<8s} {message}', style='{')

    @classmethod
    def generate_color_handler(cls, stream=sys.stdout):
        handler = logging.StreamHandler(stream)
        handler.setFormatter(cls.FORMATTER_COLOR)

        return handler
