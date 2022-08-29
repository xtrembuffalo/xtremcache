from importlib.metadata import requires
from setuptools import setup
from pathlib import Path
import os

def __get_current_dir():
    return os.path.dirname(os.path.realpath(__file__))

def __get_install_requires(file):
    requirements = Path(os.path.join(__get_current_dir(), file)).read_text()
    return requirements.split()

setup(
    name='xtremcache',
    version='1.0.0',
    author='xtrembuffalo',
    author_email='tristan.cladet@gmail.com',
    description='Handle generic file and directories caching',
    long_description=Path(os.path.join(__get_current_dir(), 'README.md')).read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/xtrembuffalo/xtremcache',
    install_requires=__get_install_requires('dist-requirements.txt'),
    entry_points={
        'console_scripts': ['xtremcache=xtremcache.__main__:main']
    },
    tests_require=__get_install_requires('test-requirements.txt'),
    test_suite='tests'
)