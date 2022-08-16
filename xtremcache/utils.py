import hashlib
from multiprocessing.pool import ThreadPool
import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor

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
    filename = os.path.splitext(os.path.basename(path))[0]
    return os.path.join(dir, filename)

class FunctionRetry(Exception):
   pass

def timeout_exec(timeout, fn, *args, **kwargs):
    start_time = time.time()
    retry = True
    rt = False
    while retry:
        try:
            rt = fn(*args, **kwargs)
            retry = False
        except FunctionRetry as e:
            if (time.time() - start_time) > timeout:
                retry = False
                rt = e.args[0] if len(e.args) else False
    return rt