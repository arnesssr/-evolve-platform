class AdminException(Exception):
    """Base class for Admin module exceptions."""
    pass


class AdminOperationError(AdminException):
    """Raised when an admin operation fails."""
    pass


class ResellerNotFound(AdminException):
    pass


class InvalidBulkAction(AdminException):
    pass


class PayoutFailure(AdminException):
    pass


class PermissionDenied(AdminException):
    pass

