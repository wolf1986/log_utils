from setuptools import setup

setup(
    name='log_utils',
    description='Utils for generic python logging package',
    author='Willy Polychenko',
    author_email='wolf1986@gmail.com',
    url='https://github.com/wolf1986/log_utils',
    version='0.3.3',
    test_suite='nose.collector',
    tests_require=['nose'],
    packages=['log_utils', 'log_utils/data_logger'],
    install_requires=['colorama', 'colorlog']
)
