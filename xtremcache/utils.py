import hashlib
import sys
import os

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