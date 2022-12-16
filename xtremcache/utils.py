import subprocess
import hashlib
import sys
import os
import time
from pathlib import Path
from typing import Any, Callable, List

from xtremcache.exceptions import *


def xtremcache_location() -> str:
    """Return the path to xtremcache dir."""

    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

def str_to_md5(val: str) -> str:
    """Hash a string thanks to md5 algo."""

    return hashlib.md5(val.encode()).hexdigest()

def isUnix() -> bool:
    """Return True if the building is an Unix at compilation time."""

    return not ('win' in sys.platform)

def timeout_exec(timeout: int, fn: Callable, *args, **kwargs) -> Any:
    """Try to execute fn and relaunch it if the FunctionRetry signal is raised and some time are left."""

    start_time = time.time()
    retry = True
    while retry:
        try:
            return fn(*args, **kwargs)
        except FunctionRetry as e:
            if timeout and (time.time() - start_time) > timeout:
                retry = False
                raise XtremCacheTimeoutError(f'{fn.__name__} timeout: {e}')

def remove_file(file: str) -> None:
    if isUnix():
        command = [
            'rm',
            '-rf',
            file
        ]
    else:
       command = [
            'cmd',
            '/C',
            'RD' if os.path.isdir(file) else 'DEL',
            '/S',
            '/Q',
            file
       ]
    subprocess.run(command, check=True)
