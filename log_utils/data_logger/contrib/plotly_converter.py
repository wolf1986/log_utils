from log_utils.data_logger.converters import DataConverterBase
from plotly.offline import plot


class PlotlyFigure:
    def __init__(self, data, layout):
        self.plotly_dict = dict(data=data, layout=layout)


class PlotlyConverter(DataConverterBase):
    def __init__(self):
        super().__init__()
        self.suggested_extension = '.html'

    def is_supported(self, obj) -> bool:
        return isinstance(obj, PlotlyFigure)

    def to_buffer(self, obj) -> bytes:
        str_div = plot(obj.plotly_dict, output_type='div', auto_open=False)
        return str_div.encode('utf8')
