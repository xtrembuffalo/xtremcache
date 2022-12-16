import hashlib
import os
import subprocess
import sys
import time
from typing import Any, Callable

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

def is_unix() -> bool:
    """Return True if the building is an Unix at compilation time."""

    return not ('win' in sys.platform)

def timeout_exec(timeout_sec: int, fn: Callable, *args, **kwargs) -> Any:
    """Try to execute fn and relaunch it if the FunctionRetry signal is raised and some time are left."""

    start_time = time.time()
    retry = True
    while retry:
        try:
            return fn(*args, **kwargs)
        except FunctionRecallAsked as e:
            if timeout_sec and (time.time() - start_time) > timeout_sec:
                retry = False
                raise XtremCacheTimeoutError(fn, timeout_sec, e)

def filesystem_remove(entry: str, recursive: bool = True) -> None:
    """Delete given file or directories."""

    if is_unix():
        command = [
            'rm',
            '-r' if recursive else '',
            '-f',
            entry
        ]
    else:
       command = [
            'cmd',
            '/C',
            'RD' if recursive and os.path.isdir(entry) else 'DEL',
            '/S',
            '/Q',
            entry
       ]
    subprocess.run(command, check=True)
