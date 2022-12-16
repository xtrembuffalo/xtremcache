from typing import Callable


# --- Global --- #


class XtremCacheException(Exception):
    """All xtremcache exceptions."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class XtremCacheItemNotFoundError(XtremCacheException):
    """Impossible to find item in database."""

    def __init__(self, id: str) -> None:
        msg = f'Impossible to find "{id}" in database.'
        super().__init__(msg)


class XtremCacheAlreadyCachedError(XtremCacheException):
    """Item already cached with same ID, please use force to override."""

    def __init__(self, id: str) -> None:
        msg = f'An "{id}" item is already cached. Use "--force" option if you want to overwrite it.'
        super().__init__(msg)


class XtremCacheMaxSizeCachedError(XtremCacheException):
    """No enough size to cache."""

    def __init__(self, id: str) -> None:
        msg = f'"{id}" is to big to be cached.'
        super().__init__(msg)


class XtremCacheRemoveError(XtremCacheException):
    """Impossible to remove item."""

    def __init__(self, err: Exception) -> None:
        msg = f'Impossible to remove item: {err}'
        super().__init__(msg)


class XtremCacheFileNotFoundError(XtremCacheException):
    """Impossible to find the file or directory to cache."""

    def __init__(self, path: str) -> None:
        msg = f'Impossible to find "{path}" to cache it.'
        super().__init__(msg)


class XtremCacheTimeoutError(XtremCacheException):
    """Timeout."""

    def __init__(self, fn: Callable, timeout_sec: int, err: Exception) -> None:
        msg = f'{fn.__name__} reached {timeout_sec} seconds timout: {err.__class__.__name__} - {err}'
        super().__init__(msg)


class XtremCacheInputError(XtremCacheException):
    """Command line options problem."""

    def __init__(self, msg: str) -> None:
        msg = f'Input validation error: {msg}.'
        super().__init__(msg)


class XtremCacheArchiveException(XtremCacheException):
    """All exceptions related to the archive."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class XtremCacheArchiveCreationError(XtremCacheArchiveException):
    """Impossible to create an archive of the file or directory."""

    def __init__(self, id: str, err: Exception) -> None:
        msg = f'Impossible to create an archive of "{id}": {err.__class__.__name__} - {err}'
        super().__init__(msg)


class XtremCacheArchiveExtractionError(XtremCacheArchiveException):
    """Impossible to extract archive."""

    def __init__(self, path: str, err: Exception) -> None:
        msg = f'Impossible to extract "{path}": {err.__class__.__name__} - {err}'
        super().__init__(msg)


class XtremCacheArchiveRemovingError(XtremCacheArchiveException):
    """Impossible remove archive."""

    def __init__(self, id: str, err: Exception) -> None:
        msg = f'Impossible remove archive "{id}": {err.__class__.__name__} - {err}'
        super().__init__(msg)


# --- Internal --- #


class InternalXtremCacheException(Exception):
    """Internal exceptions."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class FunctionRecallAsked(InternalXtremCacheException):
    """Signal raised to claim a recall after a timeout func executions."""

    def __init__(self, fn: Callable) -> None:
        name = getattr(callable, '__name__', 'Unknown')
        msg = f'A signal have been raised to claim a recall of {name}.'
        super().__init__(msg)
