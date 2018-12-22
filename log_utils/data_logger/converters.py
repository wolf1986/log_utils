import abc
import array
import pickle
from io import BytesIO
from typing import Optional


class DataConverterBase(metaclass=abc.ABCMeta):
    def __init__(self) -> None:
        self.suggested_extension = '.bin'

    @abc.abstractmethod
    def is_supported(self, obj) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def to_buffer(self, obj) -> Optional[bytes]:
        raise NotImplementedError()


class TextConverter(DataConverterBase):
    def __init__(self, encoding='utf8', errors='strict'):
        super().__init__()

        self.errors = errors
        self.encoding = encoding
        self.suggested_extension = '.txt'

    def is_supported(self, obj) -> bool:
        return isinstance(obj, str)

    def to_buffer(self, obj: str) -> bytes:
        return obj.encode(self.encoding, self.errors)


class BinaryConverter(DataConverterBase):
    def __init__(self):
        super().__init__()

    def is_supported(self, obj) -> bool:
        return isinstance(obj, (bytes, bytearray, array.array, memoryview))

    def to_buffer(self, obj) -> bytes:
        return obj


class PickleConverter(DataConverterBase):
    def __init__(self):
        super().__init__()

        self.suggested_extension = '.pickle'

    def to_buffer(self, obj) -> bytes:
        memory_file = BytesIO()
        pickle.dump(obj, memory_file)

        return memory_file.getvalue()

    def is_supported(self, obj) -> bool:
        return True
