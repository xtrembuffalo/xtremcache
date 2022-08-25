# --- Global --- #

class XtremCacheException(Exception):
    """All XtremCache exceptions."""
    pass

class XtremCacheItemNotFound(XtremCacheException):
    """Impossible to find item in database."""
    pass

class XtremCacheAlreadyCached(XtremCacheException):
    """Item already cached with same ID, please use force to override."""
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

class XtremCacheArchive(XtremCacheException):
    """All exceptions related to the archive."""
    pass

class XtremCacheArchiveCreationError(XtremCacheArchive):
    """Impossible to create an archive of the file or directory."""
    pass

class XtremCacheArchiveExtractionError(XtremCacheArchive):
    """Impossible to extract archive."""
    pass

class XtremCacheArchiveRemovingError(XtremCacheArchive):
    """Impossible remove archive."""
    pass

class XtremCacheInputError(XtremCacheArchive):
    """Command line options problem."""
    pass


# --- Internal --- #

class InternalXtremCacheException(Exception):
    """Internal exceptions."""
    pass

class FunctionRetry(InternalXtremCacheException):
    """Retry signal for timeout func executions."""
    pass