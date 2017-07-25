import abc
import array

from io import BytesIO

import pickle
from typing import Optional


class BinarySerializationHandlerBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self):
        super().__init__()

        self.extension = '.bin'

    @abc.abstractmethod
    def is_supported(self, obj) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def to_buffer(self, obj) -> Optional[bytes]:
        raise NotImplementedError()


class TextHandler(BinarySerializationHandlerBase):
    def __init__(self, encoding='utf8', errors='strict'):
        super().__init__()

        self.errors = errors
        self.encoding = encoding
        self.extension = '.txt'

    def is_supported(self, obj) -> bool:
        return isinstance(obj, str)

    def to_buffer(self, obj: str) -> bytes:
        return obj.encode(self.encoding, self.errors)


class BinaryHandler(BinarySerializationHandlerBase):
    def __init__(self):
        super().__init__()

    def is_supported(self, obj) -> bool:
        return isinstance(obj, (bytes, bytearray, array.array, memoryview))

    def to_buffer(self, obj) -> bytes:
        return obj


class PickleHandler(BinarySerializationHandlerBase):
    def __init__(self):
        super().__init__()

        self.extension = '.pickle'

    def to_buffer(self, obj) -> bytes:
        memory_file = BytesIO()
        pickle.dump(obj, memory_file)

        return memory_file.getvalue()

    def is_supported(self, obj) -> bool:
        return True
