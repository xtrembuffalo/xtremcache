# xtremcache

`xtremcache` is a Python package dedicated to handle generic file and directories caching.

## Installation

`xtremcache` is available on [PyPi](https://pypi.org/project/xtremcache/).

## Tests

Tests are written following `unittest` framework. Some dependencies are needed (`test-requirements.txt`). If you want to run tests, enter the following command at the root level of the package:

```bash
python -m unittest discover -s tests # All tests
python -m unittest discover -s tests/unit # Unit tests
python -m unittest discover -s tests/integration # Integration tests
```

## Module usage

### Cache and uncache example

- Create CacheManager with data location and the maximum size of this cache directory
- Cache a directory with unique id to find it lather
- Uncache with unique id to a specifique directory

```python
from xtremcache.cachemanager import CacheManager

cache_manager = CacheManager(
    cache_dir='/tmp/xtremcache',
    max_size=1000000
    )
cache_manager.cache(
    id='UUID',
    path='/tmp/dir_to_cache'
    )
cache_manager.uncache(
    id='UUID',
    path='/tmp/destination_dir'
    )
```

### Override cached example

- Create CacheManager with data location and the maximum size of this cache directory
- Cache a directory with unique id to find it lather
- Override last unique id to a new directory

```python
from xtremcache.cachemanager import CacheManager

cache_manager = CacheManager(
    cache_dir='/tmp/xtremcache',
    max_size=1000000
    )
cache_manager.cache(
    id='UUID',
    path='/tmp/dir_to_cache'
    )
cache_manager.cache(
    id='UUID',
    path='/tmp/new_dir_to_cache',
    force=True
    )
```

### Cache and clean example

- Create CacheManager with data location and the maximum size of this cache directory
- Cache a directory with unique id to find it lather
- Remove chached file

```python
from xtremcache.cachemanager import CacheManager

cache_manager = CacheManager(
    cache_dir='/tmp/xtremcache',
    max_size=1000000
    )
cache_manager.cache(
    id='UUID',
    path='/tmp/dir_to_cache'
    )
cache_manager.remove(
    id='UUID'
    )
```

### Cache and clean all example

- Create CacheManager with data location and the maximum size of this cache directory
- Cache a directory with unique id to find it lather
- Remove all chached files

```python
from xtremcache.cachemanager import CacheManager

cache_manager = CacheManager(
    cache_dir='/tmp/xtremcache',
    max_size=1000000
    )
cache_manager.cache(
    id='UUID',
    path='/tmp/dir_to_cache'
    )
cache_manager.remove_all()
```
