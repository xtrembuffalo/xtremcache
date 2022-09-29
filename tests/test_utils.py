from glob import glob
import random
import string
import os
import random

from xtremcache.utils import *

def get_illegal_chars():
    return [
        r'\\',
        r'}',
        r'{',
        r'&',
        r'%',
        r'#'
    ]

def get_id_data():
    return (
        'trunk@12594',
        '13c988d4f15e06bcdd0b0af290086a3079cdadb0',
        ' '.join(get_illegal_chars()),
        )

def get_random_text(len=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(len))

def generate_dir_to_cache(root):
    for r in range(3):
        root_dir = os.path.join(root, get_random_text())
        for n in range(3):
            sub_dir = os.path.join(root_dir, get_random_text())
            os.makedirs(sub_dir)
            if n == 2 and not isUnix():
                subprocess.run(['attrib', '+H', sub_dir], check=True)
            for m in range(3):
                file_path = os.path.join(sub_dir, f'{get_random_text()}.tmp')
                with open(file_path, 'a') as f:
                    f.write(get_random_text(100))
                if isUnix():
                    # symlink for unix
                    cwd = os.getcwd()
                    os.chdir(os.path.dirname(file_path))
                    os.symlink(os.path.basename(file_path), f'{get_random_text()}_symlink.txt')
                    os.chdir(cwd)
                elif m == 2:
                    # hidden files for win
                    subprocess.run(['attrib', '+H', file_path], check=True)
    with open(os.path.join(root_dir, f'{get_random_text()}.tmp'), 'a') as f:
        f.write(get_random_text(100))

def dircmp(dir1, dir2, excludes=[]):
    def get_all_files(dir, excludes_to_remove=[]):
        rt = {}
        for e in excludes_to_remove:
            for f in glob(e):
                remove_file(f) if os.path.isdir(f) else os.remove(f)
        for root, dirs, files in os.walk(dir, topdown=False):
            for name in files:
                file = os.path.relpath(os.path.join(root, name), dir)
                key = 'link' if os.path.islink(file) else 'file'
                rt[key]=[file] if not rt.get(key) else rt[key] + [file]
            for name in dirs:
                file = os.path.relpath(os.path.join(root, name), dir)
                key = 'dir'
                rt[key]=[file] if not rt.get(key) else rt[key] + [file]
        return rt
    return get_all_files(dir1, excludes_to_remove=excludes) == get_all_files(dir2)
