class XtremCacheException(Exception):
    """Application exceptions."""
    pass

class InternalXtremCacheException(Exception):
    """Internal exceptions."""
    pass

class FunctionRetry(InternalXtremCacheException):
    """Retry signal for timeout func executions."""
    pass