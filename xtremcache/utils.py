import subprocess
import hashlib
import sys
import os
import time
from pathlib import Path
from typing import Any, Callable, List

from xtremcache.exceptions import *


def is_executable() -> bool:
    """Call after pyinstaller in executable"""

    return getattr(sys, 'frozen', False)

def xtremcache_location() -> str:
    """Return the path to xtremcache dir."""

    if is_executable():
        return sys._MEIPASS
    else:
        return os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

def get_app_name() -> str:
    """Pulic application name."""

    return 'xtremcache'

def get_public_props(obj: object) -> List[str]:
    """List all public properties of an object."""

    return list(name for name in dir(obj) if not name.startswith('_'))

def str_to_md5(val: str) -> str:
    """Hash a string thanks to md5 algo."""

    return hashlib.md5(val.encode()).hexdigest()

def isUnix() -> bool:
    """Return True if the building is an Unix at compilation time."""

    return not ('win' in sys.platform)

def remove_file_extention(path: str) -> str:
    """Remove all the file extention at the end of a file."""

    dir = os.path.dirname(path)
    basename = os.path.basename(path)
    suffixes = Path(basename).suffixes
    for s in suffixes:
        basename = basename.replace(s, '')
    return os.path.join(dir, basename)

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
