import pickle
from io import BytesIO

# This handler is optional
# noinspection PyPackageRequirements
from matplotlib import pyplot
# noinspection PyPackageRequirements
from matplotlib.figure import Figure

from log_utils.data_logger.converters import DataConverterBase


class MatplotlibConverter(DataConverterBase):
    def __init__(self, file_format='png', should_close=True):
        """
            :param file_format: 'pickle' (for pickle serialization), or 'png', 'jpg', etc... (any matplotlib supported)
                Use None to trigger the none_format_action
        """
        super().__init__()
        self.save_fig_file_format = file_format

        self.suggested_extension = '.' + (file_format or '')
        if file_format == 'pickle':
            self.suggested_extension = '.pyplot'

        self.should_close = should_close
        self.none_format_action = lambda: pyplot.show()

    def is_supported(self, obj) -> bool:
        return isinstance(obj, Figure)

    def to_buffer(self, obj):
        fig = obj
        memory_stream = BytesIO()

        # Decide which method should be used:
        if self.save_fig_file_format is None:
            self.none_format_action()
            return None

        if self.save_fig_file_format == 'pickle':
            pickle.dump(fig, memory_stream)
        else:
            fig.savefig(memory_stream, format=self.save_fig_file_format)

        # Plots should be open to allow serialization, but should be cleaned afterwards
        if self.should_close:
            pyplot.close(fig)

        return memory_stream.getvalue()
