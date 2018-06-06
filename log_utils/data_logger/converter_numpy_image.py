import cv2
import numpy as np
from log_utils.data_logger.converters import DataConverterBase


class NumpyImageConverter(DataConverterBase):
    def __init__(self, file_format='png'):
        super().__init__()
        self.suggested_extension = '.' + file_format

    def is_supported(self, obj) -> bool:
        if not isinstance(obj, np.ndarray):
            return False
        if obj.ndim == 2:  # Single channel image
            return True
        if obj.ndim == 3 and obj.shape[2] == 3:  # Color image - B,G,R channels
            return True
        return False

    def to_buffer(self, obj) -> bytes:
        success, buffer = cv2.imencode(self.suggested_extension, obj)
        if not success:
            raise Exception("error compressing numpy image to {} format".format(self.suggested_extension))
        return buffer


