import logging
import time
from typing import List, Union, Iterable

from .handlers import DataHandlerBase


# noinspection PyPep8Naming
class DataLogger(logging.Logger):
    def __init__(self, name='', level=logging.NOTSET) -> None:
        super().__init__(name, level)

        self.handlers_data = []  # type: List[DataHandlerBase]

        self.verbose_generation_timing = False
        self.time_overhead_generation_sec = 0.0

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
            # noinspection PyProtectedMember
            super()._log(level, msg, args, **kwargs)
            return

        self._handleData(level, msg, data, self)

    def _getHierarchyDataHandlers(self) -> Iterable[DataHandlerBase]:
        handlers_data = []
        handlers_data += self.handlers_data

        # Collect data loggers from entire hierarchy
        current_parent = self.parent
        while current_parent is not None:
            if isinstance(current_parent, DataLogger):
                handlers_data += current_parent.handlers_data

            current_parent = current_parent.parent

        return handlers_data

    def _handleData(self, level, msg, data, message_logger):
        handlers = self._getHierarchyDataHandlers()

        # Remove handlers that are note enabled for this level
        handlers = [
            handler
            for handler in handlers
            if level >= handler.level
        ]

        # Prepare data only if any handlers exist
        if callable(data) and len(handlers) > 0:
            time_start_sec = time.perf_counter()
            data = data()
            time_generation = time.perf_counter() - time_start_sec
            self.time_overhead_generation_sec += time_generation

            if self.verbose_generation_timing:
                message_logger.debug(
                    'Time of in-memory log-data evaluation: {:.3f} [sec]'.format(time_generation)
                )

        for handler in handlers:
            handler.handle(level, msg, data, message_logger)

        # Log messages that were not handled
        if len(handlers) == 0:
            message_logger.log(level, '{} (No data handlers attached)'.format(msg))
