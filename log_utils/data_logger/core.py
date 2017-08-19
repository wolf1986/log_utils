import logging
from typing import List, Union

from .converters import DataConverterBase
from .handlers import DataHandlerBase


# noinspection PyPep8Naming
class DataLogger(logging.Logger):
    def __init__(self, name='', level=logging.NOTSET) -> None:
        super().__init__(name, level)

        self.converters = []  # type: List[DataConverterBase]
        self.handlers_data = []  # type: List[DataHandlerBase]

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

        self._handleData(level, msg, data, self)

    def _getHierarchyDataHandlers(self):
        handlers_data = []
        handlers_data += self.handlers_data

        if isinstance(self.parent, DataLogger):
            handlers_data += self.parent.handlers_data

        return handlers_data

    def _handleData(self, level, msg, data, message_logger):
        handlers = self._getHierarchyDataHandlers()

        for handler in handlers:
            handler.handle(level, msg, data, message_logger)

        # Log messages that were not handled
        if len(handlers) == 0:
            message_logger.log(level, '{} (No data handlers attached)'.format(msg))
