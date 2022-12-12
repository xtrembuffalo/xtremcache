# --- Global --- #

class XtremCacheException(Exception):
    """All xtremcache exceptions."""
    pass

class XtremCacheItemNotFoundError(XtremCacheException):
    """Impossible to find item in database."""
    pass

class XtremCacheAlreadyCachedError(XtremCacheException):
    """Item already cached with same ID, please use force to override."""
    pass

class XtremCacheMaxSizeCachedError(XtremCacheException):
    """No enough size to cache."""
    pass

class XtremCacheRemoveError(XtremCacheException):
    """Impossible to remove item."""
    pass

class XtremCacheFileNotFoundError(XtremCacheException):
    """Impossible to find the file or directory to cache."""
    pass

class XtremCacheTimeoutError(XtremCacheException):
    """Timeout."""
    pass

class XtremCacheArchiveException(XtremCacheException):
    """All exceptions related to the archive."""
    pass

class XtremCacheArchiveCreationError(XtremCacheArchiveException):
    """Impossible to create an archive of the file or directory."""
    pass

class XtremCacheArchiveExtractionError(XtremCacheArchiveException):
    """Impossible to extract archive."""
    pass

class XtremCacheArchiveRemovingError(XtremCacheArchiveException):
    """Impossible remove archive."""
    pass

class XtremCacheInputError(XtremCacheArchiveException):
    """Command line options problem."""
    pass


# --- Internal --- #

class InternalXtremCacheException(Exception):
    """Internal exceptions."""
    pass

class FunctionRetry(InternalXtremCacheException):
    """Retry signal for timeout func executions."""
    pass
