from pathlib import Path

from setuptools import setup

setup(
    name='log_utils',
    description='Utils for generic python logging package',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    author='Willy Polychenko',
    author_email='wolf1986@gmail.com',
    url='https://github.com/wolf1986/log_utils',
    version='0.4.0',
    packages=[
        'log_utils',
        'log_utils/data_logger',
        'log_utils/data_logger/contrib'
    ],
    install_requires=['colorama', 'colorlog']
)
