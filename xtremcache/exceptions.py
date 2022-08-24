# --- Global --- #

class XtremCacheException(Exception):
    """Application exceptions."""
    pass

class XtremCacheItemNotFound(XtremCacheException):
    """Impossible to find item in database."""
    pass

class XtremCacheAlreadyCached(XtremCacheException):
    """Impossible to find item in database."""
    pass

class XtremCacheRemoveError(XtremCacheException):
    """Impossible to find item in database."""
    pass

class XtremCacheFileNotFoundError(XtremCacheException):
    """Impossible to find item in database."""
    pass

class XtremCacheTimeoutError(XtremCacheException):
    """Impossible to find item in database."""
    pass

class XtremCacheArchive(XtremCacheException):
    """Impossible to find item in database."""
    pass

class XtremCacheArchiveCreationError(XtremCacheArchive):
    """Impossible to find item in database."""
    pass

class XtremCacheArchiveExtractionError(XtremCacheArchive):
    """Impossible to find item in database."""
    pass

class XtremCacheArchiveRemovingError(XtremCacheArchive):
    """Impossible to find item in database."""
    pass

class XtremCacheInputError(XtremCacheArchive):
    """Impossible to find item in database."""
    pass


# --- Internal --- #

class InternalXtremCacheException(Exception):
    """Internal exceptions."""
    pass

class FunctionRetry(InternalXtremCacheException):
    """Retry signal for timeout func executions."""
    pass