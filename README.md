# xtremcache

`xtremcache` is a Python package dedicated to handle generic file caching.

## Installation

`xtremcache` is available on [PyPi](https://pypi.org/project/xtremcache/).

# Contributions

## Tests

Tests are written following `unittest` framework. Some dependencies are needed (`test-requirements.txt`). If you want to run tests, enter the following command at the root level of the package:

```bash
python -m unittest discover
```

## Build the project

To perform the build, you need to install `dist-requirements.txt` list of packages, then run the following command. All the files will be located in `dist` directory.

```bash
python -m build
```

## Upload the project

The project can be uploaded using twine (listed in `dist-requirements.txt`) by running the following command:

```bash
python -m twine upload dist/*
```
