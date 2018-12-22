# log_utils - Utils for the generic python logging package
## Continuous Integration
- Tests are being executed continuously thanks to TravisCI
- Mastter branch: [![Build Status](https://travis-ci.com/wolf1986/log_utils.svg?branch=master)](https://travis-ci.com/wolf1986/log_utils)

## Module - LogHelper
**Sample:**  
Create a preconfigured logger format that supports colors (using colorama & colorlog packages)
```python
import logging  
from log_utils.helper import LogHelper

logger = logging.getLogger()
logger.addHandler(LogHelper.generate_color_handler())
logger.setLevel(logging.INFO)

logger.debug('Sample Message')
logger.info('Sample Message, generated timestamp: ' + LogHelper.timestamp(with_ms=True))
logger.warning('Sample Message')
logger.error('Sample Message')
logger.critical('Sample Message')
```

**Expected output:**
```python
2018-12-22 12:12:23,518 root: INFO Sample Message, using timestamp: 20181222_121223.518
2018-12-22 12:12:23,518 root: WARNING Sample Message
2018-12-22 12:12:23,518 root: ERROR Sample Message
2018-12-22 12:12:23,518 root: CRITICAL Sample Message
```

## Module - DataLogger
DataLogger implements a Logger in every sense, but adds to it the ability to receive the **optional** kwarg: `data=...`, if such arg is received, then it might be processesed by the logger for future reference.

**Features**:
1. The data will be saved only if the log level is matched (same as the logged message)
2. `data` may also be of type `Callable` - to prevent generation of data when loglevel is not matched. e.g. `..., data=lambda: generate_my_matplotlib_figure()`
3. `data` is a Python object that needs to be converted to `bytes`. See available converters ():
    1. Pure Python - TextConverter, BinaryConverter, PickleConverter
    2. Contribute to other libraries - NumpyImageConverter, MatplotlibConverter, PlotlyConverter
4. `bytes` converted from the `data` object are handled by DataHandlers (similarly to regular logger Handlers).
5. A useful handler exists (`SaveToDirHandler`), but others can be implemented for other purposes such as sending to a server.

> **Note:** Even though the module contains converters for Matplotlib and NumPy, they are only required if the user wishes to use them, so in order to successfully import these converters make sure that you have matplotlib and numpy installed.

**Sample - Nominal use case:**
```python
"""  
nternal components are responsible for their logs, the user of those components is responsible 
for handlers of the log (both text handlers such as stdout / file, and data loggers), and the 
location for writing data files created by the log. 
"""  
from log_utils.helper import LogHelper
from log_utils.data_logger import DataLogger  
from log_utils.data_logger.converter_numpy_image import NumpyImageConverter  
from log_utils.data_logger.converter_matplotlib import MatplotlibConverter  
from log_utils.data_logger.handlers import SaveToDirHandler  

# Configure a data logger - Where to save, and what conversion methods to use, propagate to text logger  
root_logger = logging.getLogger()
root_logger.addHandler(LogHelper.generate_color_handler())

logger = DataLogger('TestScript', logging.DEBUG)  
logger.addHandler(  
    SaveToDirHandler(path_dir_logs)  
        .addConverter(MatplotlibConverter())  
        .addConverter(NumpyImageConverter())  
)  
logger.parent = logger_root  

# Log data, repeat with different settings  
obj = DemoComponent()  
obj.logger.parent = logger  

logger.info('About to demo using default settings')  
obj.some_method()   

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
```
**Expected output:**
```python
2018-12-22 14:15:00,401 TestScript: INFO About to demo using default settings
2018-12-22 14:15:00,401 DemoComponent: WARNING TEST Warning
2018-12-22 14:15:00,401 DemoComponent: WARNING TEST Data Warning (No supported converters)
2018-12-22 14:15:00,401 DemoComponent: ERROR TEST Error
2018-12-22 14:15:00,403 DemoComponent: INFO About to generate and dump some string data
2018-12-22 14:15:00,403 DemoComponent: DEBUG Some string data (No supported converters)
2018-12-22 14:15:00,403 DemoComponent: INFO About to dump some binary data
2018-12-22 14:15:00,403 DemoComponent: DEBUG Some binary data (No supported converters)
2018-12-22 14:15:00,403 DemoComponent: INFO About to generate and dump some NumPy data
2018-12-22 14:15:00,403 DemoComponent: DEBUG Some numpy raw (No supported converters)
2018-12-22 14:15:00,403 DemoComponent: DEBUG Some numpy bytes (No supported converters)
2018-12-22 14:15:00,403 DemoComponent: INFO About to generate and dump a matplotlib figure
2018-12-22 14:15:00,965 DemoComponent: DEBUG Matplotlib Figure (Saved to: "C:\Users\wolf1\AppData\Local\Temp\tmp8fne_uz5\20181222_141500.889 DEBUG Matplotlib Figure.png"); I/O: 0.075 [sec]
2018-12-22 14:15:00,965 DemoComponent: INFO About to generate and dump a numpy image (50x50 gradient image)
2018-12-22 14:15:00,967 DemoComponent: DEBUG Numpy image (Saved to: "C:\Users\wolf1\AppData\Local\Temp\tmp8fne_uz5\20181222_141500.965 DEBUG Numpy image.png"); I/O: 0.001 [sec]
```

**Visit the tests for more:** 
- TextConverter
- BinaryConverter
- PickleConverter

## Module - DataLogger.contrib
In addition to Matplotlib figures and NumPy images which are supported by default, the contrib module contains additional adapters to various frameworks.

- **Plotly -** Generated figures can be saved as `.html` files for later preview in the browser. Use the `PlotlyConverter()` from `log_utils.data_logger.contrib.plotly_converter`
### Sample - Plotly
```python
import shutil

import numpy as np
import logging
from pathlib import Path
from tempfile import mkdtemp
from unittest import TestCase

from log_utils.data_logger import DataLogger

from log_utils.data_logger.contrib.plotly_converter import PlotlyConverter, PlotlyFigure
from log_utils.data_logger.handlers import SaveToDirHandler
from log_utils.helper import LogHelper


class TestPlotlyConverter(TestCase):
    @classmethod
    def get_default_grid_settings(cls, title):
        axis = dict(
            showbackground=True,
            backgroundcolor="rgb(230, 230,230)",
            gridcolor="rgb(255, 255, 255)",
            zerolinecolor="rgb(255, 255, 255)"
        )

        layout = dict(
            title=title,
            font=dict(family='Balto'),
            showlegend=False,
            width=800,
            height=800,
            scene=dict(
                xaxis=axis,
                yaxis=axis,
                zaxis=axis,
                aspectratio=dict(
                    x=1,
                    y=1,
                    z=1
                )
            )
        )

        return layout

    def test_save_ones_volume(self):
        """
            Note: For nosetest: Run with --nocapture
        """

        path_dir_logs = Path(mkdtemp())

        try:
            logger = DataLogger('TestLogger', logging.INFO)

            logger.addHandler(SaveToDirHandler(path_dir_logs).addConverter(PlotlyConverter()))
            logger.addHandler(LogHelper.generate_color_handler())

            meshes = {'i': np.array([2, 2]), 'showscale': False, 'opacity': 0.3, 'k': np.array([0, 1]),
                      'z': np.array([1., 1., 1., 1.], dtype=np.float32), 'name': '',
                      'y': np.array([0., 0., 1., 1.], dtype=np.float32),
                      'colorscale': [[0, 'rgb(6, 236, 35)'], [1.0, 'rgb(6, 236, 35)']],
                      'x': np.array([0., 1., 0., 1.], dtype=np.float32), 'type': 'mesh3d', 'j': np.array([1, 3]),
                      'reversescale': False,
                      'intensity': np.array([-0., -0.13533528, -0., -0.04978707], dtype=np.float32)
                      }
            logger.info(
                'Plotly figure sample',
                data=PlotlyFigure(data=[meshes], layout=self.get_default_grid_settings("test"))
            )

            self.assertTrue(
                len(list(path_dir_logs.glob('*.html'))) == 1
            )

        finally:
            shutil.rmtree(str(path_dir_logs))
```
