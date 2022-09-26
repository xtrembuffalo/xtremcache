from importlib.metadata import requires
from setuptools import setup
from pathlib import Path
import os

def __get_install_requires(rtype):
    requirements = Path(f"{rtype}-requirements.txt").read_text()
    return requirements.split()

setup(
    name='xtremcache',
    version='1.0.0',
    author='xtrembuffalo',
    author_email='tristan.cladet@gmail.com',
    description='Handle generic file and directories caching',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/xtrembuffalo/xtremcache',
    install_requires=__get_install_requires('dist'),
    entry_points={
        'console_scripts': ['xtremcache=xtremcache.__main__:main']
    },
    tests_require=__get_install_requires('test'),
    test_suite='tests'
)