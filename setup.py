from distutils.core import setup

setup(
    name='log_utils',
    version='0.1.0',
    test_suite='nose.collector',
    tests_require=['nose'],
    packages=['log_utils'],
    requires=['colorama', 'colorlog']
)
