import datetime
import logging
import logging.handlers
import os

import sys

import colorama
from colorlog import colorlog

if 'PYCHARM_HOSTED' in os.environ:
    colorama.deinit()


class LogHelper:
    FORMATTER_COLOR = colorlog.ColoredFormatter('{log_color}{asctime} {name}: {levelname} {message}', style='{')
    FORMATTER = logging.Formatter('{asctime} {name}: {levelname} {message}', style='{')

    @classmethod
    def generate_color_handler(cls, stream=sys.stdout):
        handler = logging.StreamHandler(stream)
        handler.setFormatter(cls.FORMATTER_COLOR)

        return handler

    @classmethod
    def get_script_name(cls):
        script_name = os.path.basename(sys.argv[0])
        script_name, _ = os.path.splitext(script_name)

        return script_name

    @classmethod
    def generate_simple_rotating_file_handler(cls, path_log_file=None, when='midnight', files_count=7):
        if path_log_file is None:
            path_dir = os.path.dirname(sys.argv[0])
            path_log_file = cls.suggest_script_log_name(path_dir)

        handler = logging.handlers.TimedRotatingFileHandler(path_log_file, when=when, backupCount=files_count)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(cls.FORMATTER)

        return handler

    @classmethod
    def suggest_script_log_name(cls, path_dir):
        return os.path.join(path_dir, cls.get_script_name() + '.log')

    @staticmethod
    def timestamp(with_ms=False, time=None):
        if time is None:
            time = datetime.datetime.now()

        if with_ms:
            return time.strftime('%Y%m%d_%H%M%S.%f')[:-3]
        else:
            return time.strftime('%Y%m%d_%H%M%S')
