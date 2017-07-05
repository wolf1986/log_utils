from distutils.core import setup

setup(
    name='log_utils',
    version='0.2.0',
    test_suite='nose.collector',
    tests_require=['nose'],
    packages=['log_utils', 'log_utils/data_logger'],
    install_requires=['colorama', 'colorlog']
)
