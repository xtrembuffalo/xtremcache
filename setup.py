import os
from pathlib import Path
from setuptools import setup
from functools import lru_cache

@lru_cache
def get_globvars_from_py_script(path):
    version={}
    exec(Path(path).read_text(), version)
    return version

@lru_cache
def get_version_info(item):
    return get_globvars_from_py_script(os.path.join('xtremcache', 'version.py'))[item]

@lru_cache
def get_long_description():
    return Path('README.md').read_text()

@lru_cache
def get_install_requires():
    return Path(f'dist-requirements.txt').read_text().split()
    
setup(
    name=get_version_info('__app_name__'),
    version=get_version_info('__version__'),
    author=get_version_info('__author__'),
    author_email='tristan.cladet@gmail.com',
    description='Handle generic file and directories caching',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    license='GPL-3.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
        'Topic :: System :: Archiving',
        'Typing :: Typed',
    ],
    keywords='cache caching store storage file files folder folders archive archives rep repertory repertories',
    project_urls={
        'Documentation': 'https://github.com/xtrembuffalo/xtremcache/blob/main/README.md',
        'Source': 'https://github.com/xtrembuffalo/xtremcache',
        'Tracker': 'https://github.com/xtrembuffalo/xtremcache/issues',
    },
    install_requires=get_install_requires(),
    entry_points={
        'console_scripts': ['xtremcache=xtremcache.__main__:main']
    },
    data_files=[
        (
            os.path.join('..','..','xtremcache','ext','msys2','zip','v3.0','bin'),
            [
                os.path.join('xtremcache','ext','msys2','zip','v3.0','bin','zip.exe'),
                os.path.join('xtremcache','ext','msys2','zip','v3.0','bin','msys-2.0.dll'),
                os.path.join('xtremcache','ext','msys2','zip','v3.0','bin','msys-bz2-1.dll'),
            ]
        ),
        (
            os.path.join('..','..','xtremcache','ext','msys2','unzip','v6.00','bin'),
            [
                os.path.join('xtremcache','ext','msys2','unzip','v6.00','bin','unzip.exe'),
                os.path.join('xtremcache','ext','msys2','unzip','v6.00','bin','msys-2.0.dll'),
                os.path.join('xtremcache','ext','msys2','unzip','v6.00','bin','msys-bz2-1.dll'),
            ]
        ),
        (
            os.path.join('..','..'),
            [
                'dist-requirements.txt',
                'README.md'
            ]
        )
    ],
    python_requires='>=3.8',
    tests_require=get_install_requires(),
    test_suite='tests')
