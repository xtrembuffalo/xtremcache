import hashlib
import sys
import os
import time
from pathlib import Path

from xtremcache.exceptions import *


def get_app_name():
    """Pulic application name."""

    return 'xtremcache'

def get_public_props(obj):
    """List all public properties of an object."""

    return list(name for name in dir(obj) if not name.startswith('_'))

def str_to_md5(val):
    """Hash a string thanks to md5 algo."""

    return hashlib.md5(val.encode()).hexdigest()

def isUnix():
    """Return True if the building is an Unix at compilation time."""

    return not ('win' in sys.platform)

def remove_file_extention(path):
    """Remove all the file extention at the end of a file."""

    dir = os.path.dirname(path)
    basename = os.path.basename(path)
    suffixes = Path(basename).suffixes
    for s in suffixes:
        basename = basename.replace(s, '')
    return os.path.join(dir, basename)

def timeout_exec(timeout, fn, *args, **kwargs):
    """Try to execute fn and relaunch it if the FunctionRetry signal is raised and some time are left."""

    start_time = time.time()
    retry = True
    while retry:
        try:
            return fn(*args, **kwargs)
        except FunctionRetry as e:
            if timeout and (time.time() - start_time) > timeout:
                retry = False
                raise XtremCacheTimeoutError(e)
