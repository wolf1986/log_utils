import logging
from unittest import TestCase

from log_utils.helper import LogHelper


class TestHelper(TestCase):
    def test_nominal(self):
        """
            Note: For nosetest: Run with --nocapture
        """

        logger = logging.getLogger()
        logger.addHandler(LogHelper.generate_color_handler())
        logger.setLevel(logging.INFO)

        logger.debug('Sample Message')
        logger.info('Sample Message, generated timestamp: ' + LogHelper.timestamp(with_ms=True))
        logger.warning('Sample Message')
        logger.error('Sample Message')
        logger.critical('Sample Message')


if __name__ == '__main__':
    TestHelper().test_nominal()
