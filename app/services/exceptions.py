"""Domain exceptions for HRMS services.

API and agent layers map these to HTTP status codes / tool error messages.
Services should raise these instead of FastAPI HTTPException.
"""


class HRMSError(Exception):
    """Base error for all domain failures."""

    def __init__(self, message: str = "An HRMS error occurred"):
        self.message = message
        super().__init__(message)


class NotFoundError(HRMSError):
    """Requested resource does not exist."""


class ForbiddenError(HRMSError):
    """Caller is not allowed to access or mutate this resource."""


class ValidationError(HRMSError):
    """Business or input validation failed."""


class InsufficientLeaveBalance(ValidationError):
    """Employee does not have enough leave balance for the request."""


class InvalidLeaveState(ValidationError):
    """Leave request is not in a state that allows this action (e.g. cancel)."""
