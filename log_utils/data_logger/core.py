import logging
import os
import pickle
import time
from io import BytesIO
from pathlib import Path
from typing import List, Union, Optional

from log_utils.helper import LogHelper

from .handlers import DataHandlerBase


# noinspection PyPep8Naming
class DataLogger(logging.Logger):
    def __init__(self, name='', path_dir=None, level=logging.NOTSET) -> None:
        super().__init__(name, level)

        self.path_generator = PathGeneratorDefault(path_dir)  # type: PathGeneratorBase

        if self.path_generator.is_enabled():
            os.makedirs(str(self.path_generator.path_dir), exist_ok=True)

        self.handlers_data = []  # type: List[DataHandlerBase]
        self.handler_data_default = None  # type: DataHandlerBase

        self.verbose_generation_timing = False

        self.time_overhead_generation_sec = 0.0
        self.time_overhead_io_sec = 0.0

    def addHandler(self, handler: Union[logging.Handler, DataHandlerBase]):
        """
            :param handler: Either a regular log handler, or a data handler
        """
        if isinstance(handler, DataHandlerBase):
            self.handlers_data.append(handler)
        else:
            super().addHandler(handler)

    def _log(self, level, msg, args, **kwargs):
        data = kwargs.pop('data', None)

        # Revert to simple logging without data - if no data was given
        if data is None:
            super()._log(level, msg, args, **kwargs)
            return

        self._logData(level, msg, data, self, args, **kwargs)

    # noinspection PyProtectedMember
    def _logData(self, level, msg, data, message_logger, args, **kwargs):
        # Prepare data only if any handlers exist
        if callable(data) and len(self.handlers_data) > 0:
            time_start_sec = time.perf_counter()
            data = data()
            time_generation = time.perf_counter() - time_start_sec
            self.time_overhead_generation_sec += time_generation

            if self.verbose_generation_timing:
                message_logger.debug(
                    'Time of in-memory log-data evaluation: {:.3f} [sec]'.format(time_generation)
                )

        # Use available handlers to translate object to bytes, and write them to files
        handlers_supported = self._getSupportedDataHandlers(data)
        path_file_without_extension = self.path_generator.generate(level, msg, '')
        for handler in handlers_supported:
            time_start_sec = time.perf_counter()
            buffer = handler.to_buffer(data)

            # Save data if handler returned bytes
            if buffer is not None and path_file_without_extension is not None:
                path_file = path_file_without_extension.with_name(path_file_without_extension.name + handler.extension)
                path_file.write_bytes(buffer)
                time_io = time.perf_counter() - time_start_sec
                msg_handler = "{} (Saved to: \"{}\"); I/O: {:.3f} [sec]".format(msg, path_file, time_io)
            else:
                time_io = time.perf_counter() - time_start_sec
                msg_handler = "{} (Not saved)".format(msg)

            self.time_overhead_io_sec += time_io
            message_logger._log(level, msg_handler, args, **kwargs)

        handled_by_parent = False
        if isinstance(self.parent, DataLogger):
            handled_by_parent = self.parent._logData(level, msg, data, message_logger, args, **kwargs)

        # Log messages that were not handled
        if len(handlers_supported) == 0 and not handled_by_parent:
            message_logger._log(level, '{} (No supported data handlers)'.format(msg), args, **kwargs)

        return handled_by_parent or len(handlers_supported) > 0

    def _getSupportedDataHandlers(self, data) -> List[DataHandlerBase]:
        handlers_supported = []  # type:
        for handler in self.handlers_data:
            if handler.is_supported(data):
                handlers_supported.append(handler)
        if len(handlers_supported) == 0 and self.handler_data_default is not None:
            handlers_supported.append(self.handler_data_default)

        return handlers_supported


class PickleHandler(DataHandlerBase):
    def __init__(self):
        super().__init__()

        self.extension = '.pickle'

    def to_buffer(self, obj) -> bytes:
        memory_file = BytesIO()
        pickle.dump(obj, memory_file)

        return memory_file.getvalue()

    def is_supported(self, obj) -> bool:
        return True


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
    def __init__(self, path_dir: Union[Optional[Path], str]):
        self.path_dir = path_dir
        self.prefix_generator = None  # type: PrefixGeneratorBase

    def is_enabled(self) -> bool:
        return self.path_dir is not None

    def generate(self, level: int, title: str, extension: str) -> Path:
        raise NotImplementedError()


class PathGeneratorDefault(PathGeneratorBase):
    def __init__(self, path_dir):
        super().__init__(path_dir)

        self.prefix_generator = PrefixGeneratorTimestamp()
        self.use_log_level = True

    def generate(self, level: int, title: str, extension: str) -> Optional[Path]:
        if not self.is_enabled():
            return None

        str_log_level = ''
        if self.use_log_level:
            str_log_level = logging.getLevelName(level) + ' '

        filename = self.prefix_generator.generate() + str_log_level + title + extension
        return Path(self.path_dir, filename)
