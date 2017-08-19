import abc
import logging
import os
import re
import time
from pathlib import Path
from typing import Union, Optional, List

from .converters import DataConverterBase
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

        self.sanitize_filenames = True
        self.prefix_generator = PrefixGeneratorTimestamp()
        self.use_log_level = True

    @staticmethod
    def sanitize_filename(string: str) -> str:
        def remove_chars_re(subj, chars):
            return re.sub('[' + re.escape(''.join(chars)) + ']', '_', subj)

        return remove_chars_re(string, ':\\?<>|/%')

    def generate(self, level: int, title: str, extension: str) -> Optional[Path]:
        if not self.is_enabled():
            return None

        str_log_level = ''
        if self.use_log_level:
            str_log_level = logging.getLevelName(level) + ' '

        filename = self.prefix_generator.generate() + str_log_level + title + extension

        if self.sanitize_filenames:
            filename = self.sanitize_filename(filename)

        return Path(self.path_dir, filename)


# noinspection PyPep8Naming
class DataHandlerBase(metaclass=abc.ABCMeta):
    def __init__(self):
        self.converters = []

    def addConverter(self, converter: DataConverterBase) -> 'DataHandlerBase':
        """
            :return: Returns self instance to allow chaining pattern
        """
        self.converters.append(converter)

        return self

    @abc.abstractmethod
    def handle(self, level, msg, data, logger) -> None:
        raise NotImplementedError()

    def _getSupportedConverters(self, data) -> List[DataConverterBase]:
        converters_supported = []  # type:
        for converter in self.converters:
            if converter.is_supported(data):
                converters_supported.append(converter)

        return converters_supported


class SaveToDirHandler(DataHandlerBase):
    def __init__(self, path_dir: Union[Path, str]) -> None:
        super().__init__()

        self.path_generator = PathGeneratorDefault(path_dir)  # type: PathGeneratorBase
        self.time_overhead_io_sec = 0.0
        self.should_overwrite = True

        os.makedirs(str(self.path_generator.path_dir), exist_ok=True)

    def handle(self, level, msg, data_obj, logger: logging.Logger) -> None:
        # Use available converters to translate object to bytes, and pass them to handlers
        converters_supported = self._getSupportedConverters(data_obj)
        path_file_without_extension = self.path_generator.generate(level, msg, '')
        for converter in converters_supported:
            time_start_sec = time.perf_counter()
            buffer = converter.to_buffer(data_obj)

            # Save data if handler returned bytes
            if buffer is not None and path_file_without_extension is not None:
                path_file = path_file_without_extension.with_name(
                    path_file_without_extension.name + converter.suggested_extension)

                is_written_successfully = False
                # noinspection PyBroadException
                try:
                    if not self.should_overwrite and path_file.exists():
                        raise Exception('File already exist, overwrite disallowed')

                    path_file.write_bytes(buffer)
                    is_written_successfully = True
                except Exception as e:
                    logger.log(level, "{} (Unable to save; Exception: {})".format(msg, str(e)))
                finally:
                    time_io = time.perf_counter() - time_start_sec
                    if is_written_successfully:
                        logger.log(level, "{} (Saved to: \"{}\"); I/O: {:.3f} [sec]".format(msg, path_file, time_io))

            else:
                time_io = time.perf_counter() - time_start_sec
                logger.log(level, "{} (Not saved)".format(msg))

            self.time_overhead_io_sec += time_io

        if len(converters_supported) == 0:
            logger.log(level, msg + ' (No supported converters)')
