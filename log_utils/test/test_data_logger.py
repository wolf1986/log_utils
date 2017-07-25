import logging
import shutil
from pathlib import Path
from tempfile import mkdtemp
from unittest import TestCase

# noinspection PyPackageRequirements
import numpy as np
# noinspection PyPackageRequirements
from matplotlib import pyplot, mlab

from log_utils.data_logger import DataLogger
from log_utils.data_logger.core import PrefixGeneratorCounting, PrefixGeneratorTimestamp
from log_utils.data_logger.handler_matplotlib import MatplotlibHandler
from log_utils.data_logger.handlers import TextHandler, BinaryHandler, PickleHandler
from log_utils.helper import LogHelper


class TestDataLogger(TestCase):
    def test_nominal(self):
        """
            Note: For nosetest: Run with --nocapture
        """

        path_dir_temp = Path(mkdtemp())
        try:
            logger = logging.getLogger()
            logger.addHandler(LogHelper.generate_color_handler())
            logger.setLevel(logging.DEBUG)

            logger_data = DataLogger('some_data_logger', path_dir_temp)
            logger_data.parent = logger

            logger_data.log_generation_timing = True
            logger_data.path_generator.prefix_generator = PrefixGeneratorTimestamp()
            logger_data.handler_data_default = PickleHandler()
            logger_data.setLevel(logging.DEBUG)
            # logger_data.addHandler(LogHelper.generate_color_handler())

            logger_data.handlers_data.append(TextHandler(encoding='utf8'))
            logger_data.handlers_data.append(BinaryHandler())
            logger_data.handlers_data.append(MatplotlibHandler())

            logger.info('About to generate and dump some string data')
            logger_data.debug('Some string data', data=lambda: 'File Contents\nLine 2')

            logger.info('About to dump some binary data')
            logger_data.info('Some binary data', data=b'File Contents\nLine 2')

            logger.info('About to generate and dump some NumPy data')
            logger_data.info('Some numpy data', data=np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))

            logger.info('About to generate and dump a matplotlib figure')
            logger_data.info('Matplotlib Figure', data=lambda: self.figure_visualization())

        finally:
            shutil.rmtree(str(path_dir_temp))

    @staticmethod
    def figure_visualization():
        np.random.seed(0)

        # example data
        mu = 100  # mean of distribution
        sigma = 15  # standard deviation of distribution
        x = mu + sigma * np.random.randn(437)

        num_bins = 50
        fig, ax = pyplot.subplots()

        # the histogram of the data
        n, bins, patches = ax.hist(x, num_bins, normed=1)

        # add a 'best fit' line
        y = mlab.normpdf(bins, mu, sigma)
        ax.plot(bins, y, '--')
        ax.set_xlabel('Smarts')
        ax.set_ylabel('Probability density')
        ax.set_title(r'Histogram of IQ: $\mu=100$, $\sigma=15$')

        # Tweak spacing to prevent clipping of ylabel
        fig.tight_layout()

        return fig


if __name__ == '__main__':
    TestDataLogger().test_nominal()
