import logging
import logging.handlers
import shutil
from pathlib import Path
from tempfile import mkdtemp
from unittest import TestCase

# noinspection PyPackageRequirements
import numpy as np
# noinspection PyPackageRequirements
from matplotlib import pyplot, mlab

from log_utils.data_logger import DataLogger
from log_utils.data_logger.converter_numpy_image import NumpyImageConverter
from log_utils.data_logger.handlers import PrefixGeneratorCounting, SaveToDirHandler
from log_utils.data_logger.converter_matplotlib import MatplotlibConverter
from log_utils.data_logger.converters import TextConverter, BinaryConverter, PickleConverter
from log_utils.helper import LogHelper

logger_root = logging.getLogger()
logger_root.addHandler(LogHelper.generate_color_handler())
logger_root.setLevel(logging.DEBUG)


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

    def test_nominal(self):
        """
            Internal components are responsible for their logs, the user of those components is responsible for
             handlers of the log (both text handlers such as stdout / file, and data loggers), and the location for
             writing data files created by the log.
        """
        path_dir_logs = Path(mkdtemp())
        try:
            # Configure a data logger - Where to save, and what conversion methods to use, propagate to text logger
            logger = DataLogger('TestScript', logging.DEBUG)
            logger.addHandler(
                SaveToDirHandler(path_dir_logs).addConverter(MatplotlibConverter()).addConverter(NumpyImageConverter())
            )
            logger.parent = logger_root

            # Log data, repeat with different settings
            obj = DemoComponent()
            obj.logger.parent = logger

            logger.info('About to demo using default settings')
            obj.some_method()

        finally:
            shutil.rmtree(str(path_dir_logs))

    def test_full_functionality(self):
        path_dir_logs = Path(mkdtemp())

        try:
            # Configure a data logger
            logger = DataLogger('TestScript', logging.DEBUG)
            logger.parent = logger_root

            matplotlib_converter1 = MatplotlibConverter(should_close=False) # Leave plot open for followers
            matplotlib_converter1.hook_transform_figure = self.prepare_figure_for_saving

            data_handler = SaveToDirHandler(path_dir_logs)
            data_handler.addConverter(TextConverter(encoding='utf8'))
            data_handler.addConverter(BinaryConverter())
            data_handler.addConverter(matplotlib_converter1)
            data_handler.addConverter(MatplotlibConverter(file_format='pickle', should_close=True))  # Include cleanup
            data_handler.addConverter(NumpyImageConverter())
            logger.addHandler(data_handler)

            # Write to log how long does it take to evaluate the data generating function
            data_handler.verbose_generation_timing = True

            # Substitute the default timestamp prefix with a counting prefix
            data_handler.path_generator.prefix_generator = PrefixGeneratorCounting()

            # Set a default handler for data that is left unhandled
            logger.handler_data_default = PickleConverter()

            # Log data, repeat with different settings
            obj = DemoComponent()
            obj.logger.parent = logger

            logger.info('About to demo using alternative settings')

            obj.some_method()

            logger.info('Overhead cumulative times:')
            logger.info('- Evaluation time of given functions to bytes: {:.2f} [sec]'.format(
                logger.time_overhead_generation_sec
            ))
            logger.info('- Time of I/O: {:.2f} [sec]'.format(data_handler.time_overhead_io_sec))

        finally:
            shutil.rmtree(str(path_dir_logs))

    def test_full_hierarchy_logging(self):
        path_dir_logs = Path(mkdtemp())
        try:
            # Configure a data logger - Where to save, and what conversion methods to use, propagate to text logger
            logger1 = DataLogger('DataLogger1')
            logger1.addHandler(
                SaveToDirHandler(path_dir_logs).addConverter(TextConverter()).setLevel(logging.CRITICAL)
            )
            logger1.parent = logger_root

            logger2 = logging.getLogger('Logger2')
            logger2.parent = logger1

            logger3 = DataLogger('DataLogger3')
            logger3.addHandler(
                SaveToDirHandler(path_dir_logs).addConverter(TextConverter()).setLevel(logging.ERROR)
            )
            logger3.parent = logger2

            # Log data
            # Expected "no data handlers attached"
            logger3.info('Test INFO - with data', data='Test Data - Text')
            logger3.info('Test INFO - without data')

            # Expected to be handled only by data handler of logger2
            logger3.error('Test ERROR - with data', data='Test Data - Text')
            logger3.error('Test ERROR - without data')

            # Expected to be handled by data handlers of logger2 and logger1
            # Resulting in a two log-message that the data has been handled
            logger3.critical('Test CRITICAL - with data', data='Test Data - Text')
            logger3.critical('Test CRITICAL - without data')

        finally:
            shutil.rmtree(str(path_dir_logs))

    @staticmethod
    def prepare_figure_for_saving(figure):
        figure.set_size_inches(15, 10)
        pyplot.tight_layout()

        return figure


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
        np_array = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.logger.debug('Some numpy raw', data=np_array)
        self.logger.debug('Some numpy bytes', data=np_array.tobytes())

        self.logger.info('About to generate and dump a matplotlib figure')
        self.logger.debug('Matplotlib Figure', data=lambda: self.figure_visualization())

        self.logger.info('About to generate and dump a numpy image (50x50 gradient image)')
        self.logger.debug('Numpy image', data=lambda: np.meshgrid(range(0, 250, 5), range(50))[0])

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
