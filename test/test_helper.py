from unittest import TestCase
import logging

import sys

from helper import LogHelper


class TestHelper(TestCase):
    def test_nominal(self):
        """
            Note: For nosetest: Run with --nocapture
        """

        logger = logging.getLogger()
        logger.addHandler(LogHelper.generate_color_handler())
        logger.setLevel(logging.INFO)

        logger.debug('Sample Message')
        logger.info('Sample Message')
        logger.warning('Sample Message')
        logger.error('Sample Message')
        logger.critical('Sample Message')

if __name__ == '__main__':
    TestHelper().test_nominal()