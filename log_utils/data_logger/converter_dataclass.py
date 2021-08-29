import json
from dataclasses import asdict, is_dataclass

from log_utils.data_logger.converters import DataConverterBase


class DataclassConverter(DataConverterBase):
    """
        Convert dataclasses to string with a serializer such as `json.dumps(...)`
        Optionally provide your own serializer, e.g,: `dumps_function=yaml.dumps`
    """

    def __init__(self, *, dumps_function=None):
        if not dumps_function:
            dumps_function = lambda x: json.dumps(x, indent=2)

        super().__init__()
        self.indent = 2
        self.suggested_extension = '.json'
        self.dumps_function = dumps_function

    def to_buffer(self, obj) -> bytes:
        yaml_str = self.dumps_function(asdict(obj))
        return yaml_str.encode()  # as UTF8

    def is_supported(self, obj) -> bool:
        return is_dataclass(obj)
