import random
import string
import os
import random

from xtremcache.utils import *

def get_random_text(len=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(len))

def generate_dir_to_cache(root):
    for n in range(10):
        sub_dir = get_random_text() 
        for m in range(10):
            file_path = os.path.join(root, sub_dir, f"{get_random_text()}.tmp")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'a') as f:
                f.write(get_random_text(100))
            if isUnix():
                cwd = os.getcwd()
                os.chdir(os.path.dirname(file_path))
                os.symlink(os.path.basename(file_path), f"{get_random_text()}_symlink.txt")
                os.chdir(cwd)