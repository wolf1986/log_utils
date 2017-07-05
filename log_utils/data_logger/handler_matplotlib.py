import pickle
from io import BytesIO

from matplotlib import pyplot
from matplotlib.figure import Figure

from log_utils.data_logger.handlers import BinarySerializationHandlerBase


class MatplotlibHandler(BinarySerializationHandlerBase):
    def __init__(self, file_format='png'):
        """
            :param file_format: 'pickle' (for pickle serialization), or 'png', 'jpg', etc... (any matplotlib supported)
        """
        super().__init__()
        self.file_format = file_format

        self.extension = '.' + file_format
        if file_format == 'pickle':
            self.extension = '.pyplot'

    def is_supported(self, obj) -> bool:
        return isinstance(obj, Figure)

    def to_binary(self, obj) -> bytes:
        fig = obj
        memory_stream = BytesIO()

        # Decide which method should be used:
        if self.file_format == 'pickle':
            pickle.dump(fig, memory_stream)
        else:
            fig.savefig(memory_stream, format=self.file_format)
            pyplot.close(fig)

        return memory_stream.getvalue()