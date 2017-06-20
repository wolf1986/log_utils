from distutils.core import setup

setup(
    name='log_utils',
    version='0.1.0',
    modules=['helper.py', 'test/test_helper.py'],
    requires=['colorama', 'colorlog']
)
