class CollectorError(Exception):
    """Base collector exception."""
    pass


class CollectorExecutionError(CollectorError):
    """Raised when a collector fails during execution."""
    pass
