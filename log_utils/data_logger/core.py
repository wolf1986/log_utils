import logging
import time
from pathlib import Path
from typing import List

from .handlers import BinarySerializationHandlerBase
from ..helper import LogHelper


class PrefixGeneratorBase:
    def generate(self) -> str:
        raise NotImplementedError()


class PrefixGeneratorTimestamp(PrefixGeneratorBase):
    def generate(self) -> str:
        return LogHelper.timestamp(with_ms=True) + ' '


class PrefixGeneratorCounting(PrefixGeneratorBase):
    def __init__(self) -> None:
        super().__init__()

        self.digits = 3
        self.counter = 0

    def reset(self, counter_value=0):
        self.counter = counter_value

    def generate(self) -> str:
        prefix = str(self.counter).zfill(self.digits) + ' '
        self.counter += 1

        return prefix


class PathGeneratorBase:
    def __init__(self, path_dir):
        self.path_dir = Path(path_dir)
        self.prefix_generator = None  # type: PrefixGeneratorBase

    def generate(self, level: int, title: str, extension: str) -> Path:
        raise NotImplementedError()


class PathGeneratorDefault(PathGeneratorBase):
    def __init__(self, path_dir):
        super().__init__(path_dir)
        self.prefix_generator = PrefixGeneratorTimestamp()
        self.use_log_level = True

    def generate(self, level: int, title: str, extension: str) -> Path:
        str_log_level = ''
        if self.use_log_level:
            str_log_level = logging.getLevelName(level) + ' '

        filename = self.prefix_generator.generate() + str_log_level + title + extension
        return Path(self.path_dir / filename)


class DataLogger(logging.LoggerAdapter):
    def __init__(self, logger, path_dir):
        super().__init__(logger, {})

        self.path_generator = PathGeneratorDefault(path_dir)  # type: PathGeneratorBase

        self.handlers = []  # type: List[BinarySerializationHandlerBase]

        self.log_generation_timing = False

        self.time_overhead_generation_sec = 0.0
        self.time_overhead_io_sec = 0.0

        self.default_handler = None  # type: BinarySerializationHandlerBase

    def log(self, level, msg, *args, **kwargs):
        data = kwargs.pop('data', None)
        if data is None:
            raise Exception("{} must have 'data' keyword in log calls".format(self.__class__.__name__))

        # Prepare data
        if callable(data):
            time_start_sec = time.perf_counter()
            data = data()
            time_generation = time.perf_counter() - time_start_sec
            self.time_overhead_generation_sec += time_generation

            if self.log_generation_timing:
                self.logger.debug(
                    'Time of in-memory log-data generation: {:.3f} [sec]'.format(time_generation)
                )

        # Use available handlers to translate object and write to files
        handlers_supported = []
        for handler in self.handlers:
            if handler.is_supported(data):
                handlers_supported.append(handler)

        if len(handlers_supported) == 0 and self.default_handler is not None:
            handlers_supported.append(self.default_handler)

        for handler in handlers_supported:
            time_start_sec = time.perf_counter()
            path_file = self.path_generator.generate(level, msg, handler.extension)
            path_file.write_bytes(
                handler.to_binary(data)
            )
            time_io = time.perf_counter() - time_start_sec
            self.time_overhead_io_sec += time_io
            msg = "{} (Saved to: \"{}\"); I/O: {:.3f} [sec]".format(msg, path_file, time_io)

        self.logger.log(level, msg, *args, **kwargs)
