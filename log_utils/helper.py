import datetime
import io
import logging
import logging.handlers
import os
import sys
from collections import deque
from time import perf_counter

import colorlog


class LogHelper:
    FORMATTER_COLOR = colorlog.ColoredFormatter('{log_color}{asctime} {name}: {levelname} {message}', style='{')
    FORMATTER = logging.Formatter('{asctime} {name}: {levelname} {message}', style='{')

    @classmethod
    def generate_color_handler(cls, stream=sys.stdout):
        handler = logging.StreamHandler(stream)
        handler.setFormatter(cls.FORMATTER_COLOR)

        return handler

    @classmethod
    def get_script_name(cls):
        script_name = os.path.basename(sys.argv[0])
        script_name, _ = os.path.splitext(script_name)

        return script_name

    @classmethod
    def generate_simple_rotating_file_handler(cls, path_log_file=None, when='midnight', files_count=7):
        if path_log_file is None:
            path_dir = os.path.dirname(sys.argv[0])
            path_log_file = cls.suggest_script_log_name(path_dir)

        handler = logging.handlers.TimedRotatingFileHandler(path_log_file, when=when, backupCount=files_count)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(cls.FORMATTER)

        return handler

    @classmethod
    def suggest_script_log_name(cls, path_dir):
        return os.path.join(path_dir, cls.get_script_name() + '.log')

    @staticmethod
    def timestamp(with_ms=False, time=None):
        if time is None:
            time = datetime.datetime.now()

        if with_ms:
            return time.strftime('%Y%m%d_%H%M%S.%f')[:-3]
        else:
            return time.strftime('%Y%m%d_%H%M%S')


class PerformanceMetric:
    def __init__(self, *, n_samples=1000, units_suffix='', units_format='.2f', name=None):
        super().__init__()

        self.name: str = name
        self.queue_samples = deque(maxlen=n_samples)
        self.total = 0
        self.last = 0
        self.units_str = units_suffix
        self.units_format = units_format

    def reset(self):
        self.total = 0
        self.last = 0
        self.queue_samples.clear()

    @property
    def n_samples(self):
        return len(self.queue_samples)

    def __str__(self):
        str_name = f'[{self.name}] ' if self.name else ''
        if self.n_samples == 0:
            return f'{str_name}No measurements'

        return '{}Average: {:{}} {}; Last: {:{}} {}; Samples: {};'.format(
            str_name, self.average, self.units_format, self.units_str,
            self.last, self.units_format, self.units_str,
            self.n_samples
        )

    def last_str(self):
        str_name = f'[{self.name}] ' if self.name else ''
        return f'{str_name}{self.last:{self.units_format}} {self.units_str}'

    @property
    def average(self):
        if self.n_samples == 0:
            return None

        return self.total / self.n_samples

    def submit_sample(self, sample: float):
        sample_popped = 0
        if self.n_samples == self.queue_samples.maxlen:
            sample_popped = self.queue_samples.popleft()

        self.last = sample
        self.total += self.last - sample_popped

        self.queue_samples.append(self.last)


class PerformanceTimer(PerformanceMetric):
    def __init__(self, n_samples=1000, units_format='.1f', **kwargs) -> None:
        super().__init__(n_samples=n_samples, units_suffix='sec', units_format=units_format, **kwargs)

        self.time_last_start = 0

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, t, value, tb):
        self.end()

    def begin(self):
        self.time_last_start = perf_counter()

    def end(self):
        self.submit_sample(self.peek())

    def peek(self):
        return perf_counter() - self.time_last_start


class PrintStream:
    """
        Shortcut for using `StringIO`

        printf = PrintStream()
        printf('Case Results:')
        printf(...)

        string = str(printf)

    """

    def __init__(self, stream=None):
        if not stream:
            stream = io.StringIO()

        self.stream = stream

    def __call__(self, *args, **kwargs):
        print(*args, file=self.stream, **kwargs)

    def __str__(self):
        return self.stream.getvalue()
