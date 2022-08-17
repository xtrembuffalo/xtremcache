import hashlib
import sys
import os
import time
from pathlib import Path

from xtremcache.exceptions import *

def get_app_name():
    return "xtremcache"

def get_public_props(obj):
    return list(name for name in dir(obj) if not name.startswith('_'))

def str_to_md5(val):
    return hashlib.md5(val.encode()).hexdigest()

def isUnix():
    return not ('win' in sys.platform)

def remove_file_extention(path):
    dir = os.path.dirname(path)
    basename = os.path.basename(path)
    suffixes = Path(basename).suffixes
    for s in suffixes:
        basename = basename.replace(s, '')
    return os.path.join(dir, basename)

def timeout_exec(timeout, fn, *args, **kwargs):
    start_time = time.time()
    retry = True        
    while retry:
        try:
            return fn(*args, **kwargs)
        except FunctionRetry as e:
            if (time.time() - start_time) > timeout:
                retry = False
                raise XtremCacheTimeoutError(e)