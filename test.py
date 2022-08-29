from importlib.metadata import requires
from setuptools import setup
from pathlib import Path
import os

def __get_current_dir():
    return os.path.dirname(os.path.realpath(__file__))

def __get_install_requires():
    requirements = Path(os.path.join(__get_current_dir(), 'requirements.txt')).read_text()
    return '\n'.join(requirements)

print(__get_install_requires())