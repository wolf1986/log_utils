import pickle
from io import BytesIO

from matplotlib import pyplot
from matplotlib.figure import Figure

from log_utils.data_logger.handlers import BinarySerializationHandlerBase


class MatplotlibHandler(BinarySerializationHandlerBase):
    def __init__(self, file_format='png', should_close=True):
        """
            :param file_format: 'pickle' (for pickle serialization), or 'png', 'jpg', etc... (any matplotlib supported)
                Use None to trigger the none_format_action
        """
        super().__init__()
        self.file_format = file_format

        self.extension = '.' + (file_format or '')
        if file_format == 'pickle':
            self.extension = '.pyplot'

        self.should_close = should_close
        self.none_format_action = lambda: pyplot.show()

    def is_supported(self, obj) -> bool:
        return isinstance(obj, Figure)

    def to_buffer(self, obj):
        fig = obj
        memory_stream = BytesIO()

        # Decide which method should be used:
        if self.file_format is None:
            self.none_format_action()
            return None

        if self.file_format == 'pickle':
            pickle.dump(fig, memory_stream)
        else:
            fig.savefig(memory_stream, format=self.file_format)
            if self.should_close:
                pyplot.close(fig)

        return memory_stream.getvalue()
