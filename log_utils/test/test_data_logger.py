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
from log_utils.data_logger.core import PickleHandler, PrefixGeneratorCounting
from log_utils.data_logger.handler_matplotlib import MatplotlibHandler
from log_utils.data_logger.handlers import TextHandler, BinaryHandler
from log_utils.helper import LogHelper


class TestDataLogger(TestCase):
    """
        Note: To make all the logs visible, run nose tests with --nocapture
    """

    def test_silent(self):
        """
            Simplest use - Some internal component owns a logger. As long as it isn't connected to a parent logger,
             the logs are invisible (except test & error)

            As long as there are'nt any handlers to deal with the data given to the logger, there will be no overhead
              to execution time.
        """
        obj = DemoComponent()
        obj.some_method()

        obj.logger.setLevel(logging.DEBUG)

    def test_full_functionality(self):
        """
            Internal components are responsible for their logs, the user of those components is responsible for
             handlers of the log (both text handlers such as stdout / file, and data loggers), and the location for
             writing data files created by the log.
        """
        path_dir_logs = Path(mkdtemp())

        try:
            # Configure root logger - to demonstrate propagation from DataLogger to the root Logger
            logger_root = logging.getLogger()
            logger_root.addHandler(LogHelper.generate_color_handler())
            logger_root.setLevel(logging.DEBUG)

            # Configure a data logger
            logger = DataLogger('TestScript', path_dir_logs)
            logger.setLevel(logging.DEBUG)
            logger.parent = logger_root

            # Log data, repeat with different settings
            obj = DemoComponent()
            obj.logger.parent = logger

            logger.info('About to demo using default settings')
            obj.some_method()

            logger.info('About to demo using alternative settings')

            # Write to log how long does it take to evaluate the data generating function
            logger.verbose_generation_timing = True

            # Substitute the default timestamp prefix with a counting prefix
            logger.path_generator.prefix_generator = PrefixGeneratorCounting()

            # Set a default handler for data that is left unhandled
            logger.handler_data_default = PickleHandler()

            # Add data handlers
            logger.addHandler(TextHandler(encoding='utf8'))
            logger.addHandler(BinaryHandler())
            logger.addHandler(MatplotlibHandler())

            obj.some_method()

        finally:
            shutil.rmtree(str(path_dir_logs))


class DemoComponent:
    def __init__(self) -> None:
        self.logger = DataLogger(name='DemoComponent')

    def some_method(self):
        self.logger.warning('TEST Warning')
        self.logger.warning('TEST Data Warning', data=lambda: 'Some text contents')
        self.logger.error('TEST Error')

        self.logger.info('About to generate and dump some string data')
        self.logger.debug('Some string data', data=lambda: 'File Contents\nLine 2')

        self.logger.info('About to dump some binary data')
        self.logger.debug('Some binary data', data=b'File Contents\nLine 2')

        self.logger.info('About to generate and dump some NumPy data')
        self.logger.debug('Some numpy data', data=np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))

        self.logger.info('About to generate and dump a matplotlib figure')
        # self.logger.debug('Matplotlib Figure', data=lambda: self.figure_visualization())

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
    TestDataLogger().test_full_functionality()
