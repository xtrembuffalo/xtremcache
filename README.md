# xtremcache

`xtremcache` is a Python package dedicated to handle generic file and directories caching on Windows or Linux.
The goal of this module is to be able to cache a file or directory with a unique identifier of your choice and later uncache to a specific location.
The directory where the cached files are located is local.
The concurrent access (reading and writing) on chached archives is handle by a small data base located in the local data directory.

## Installation

`xtremcache` is available on [PyPi](https://pypi.org/project/xtremcache/).

## Tests

Tests are written following `unittest` framework. Some dependencies are needed (`test-requirements.txt`). If you want to run tests, enter the following command at the root level of the package:

```bash
python -m unittest discover -s tests # All tests
python -m unittest discover -s tests/unit # Unit tests
python -m unittest discover -s tests/integration # Integration tests
```

## Usage

### Cache and uncache example

- Create CacheManager with optional data location and the maximum size in Mo of this cache directory.
- Cache a directory with unique id to find it lather.
- Uncache with unique id to a specifique directory.

Python:

```python
from xtremcache.cachemanager import CacheManager

cache_manager = CacheManager(
    cache_dir='/tmp/xtremcache',
    max_size=20_000_000)
cache_manager.cache(
    id='UUID',
    path='/tmp/dir_to_cache')
cache_manager.uncache(
    id='UUID',
    path='/tmp/destination_dir')
```

Shell:

```sh
xtremcache config set cache_dir '/tmp/xtremcache' --local
xtremcache config set max_size '20m' --local
xtremcache cache --id 'UUID' '/tmp/dir_to_cache'
xtremcache uncache --id 'UUID' '/tmp/destination_dir'
```

---

### Override cached example

- Create CacheManager with data location and the maximum size in Mo of this cache directory
- Cache a directory with unique id to find it lather
- Override last unique id to a new directory

Python:

```python
from xtremcache.cachemanager import CacheManager

cache_manager = CacheManager(
    cache_dir='/tmp/xtremcache',
    max_size=20_000_000)
cache_manager.cache(
    id='UUID',
    path='/tmp/dir_to_cache')
cache_manager.cache(
    id='UUID',
    path='/tmp/new_dir_to_cache',
    force=True)
```

Shell:

```sh
xtremcache config set cache_dir '/tmp/xtremcache' --local
xtremcache config set max_size '20m' --local
xtremcache cache --id 'UUID' '/tmp/dir_to_cache'
xtremcache cache --force --id 'UUID' '/tmp/new_dir_to_cache'
```

---

### Cache and clean example

- Create CacheManager with data location and the maximum size in Mo of this cache directory
- Cache a directory with unique id to find it lather
- Remove chached file

Python:

```python
from xtremcache.cachemanager import CacheManager

cache_manager = CacheManager(
    cache_dir='/tmp/xtremcache',
    max_size='20m')
cache_manager.cache(
    id='UUID',
    path='/tmp/dir_to_cache')
cache_manager.remove(
    id='UUID')
```

Shell:

```sh
xtremcache config set cache_dir '/tmp/xtremcache' --local
xtremcache config set max_size '20m' --local
xtremcache cache --id 'UUID' '/tmp/dir_to_cache'
xtremcache remove --id 'UUID'
```

---

### Cache and clean all example

- Create CacheManager with data location and the maximum size in Mo of this cache directory
- Cache a directory with unique id to find it lather
- Remove all chached files

Python:

```python
from xtremcache.cachemanager import CacheManager

cache_manager = CacheManager(
    cache_dir='/tmp/xtremcache',
    max_size='20m')
cache_manager.cache(
    id='UUID',
    path='/tmp/dir_to_cache')
cache_manager.remove()
```

Shell:

```sh
xtremcache config set cache_dir '/tmp/xtremcache' --local
xtremcache config set max_size '20m' --local
xtremcache cache --id 'UUID' '/tmp/dir_to_cache'
xtremcache remove
```
