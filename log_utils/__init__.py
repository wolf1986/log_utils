# colorlog module will do `colorama.init()`, however for PyCharm IDE it will break colors in the console
# First import colorama to trigger the `init()` then use `deinit()` to fix this if execution is hosted by PyCharm

import os

import colorama
# noinspection PyUnresolvedReferences
import colorlog

if 'PYCHARM_HOSTED' in os.environ:
    colorama.deinit()
