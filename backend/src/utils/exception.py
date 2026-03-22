from typing import Optional


class ApiError(Exception):
    status_code: int = 500
    default_error_code: str = "INTERNAL_SERVER_ERROR"

    def __init__(self, error_code: Optional[str] = None, message: Optional[str] = None):
        self.error_code = error_code or self.default_error_code
        self.message = message
        super().__init__(self.message)


class NotFound(ApiError):

    status_code = 404
    default_error_code = "NOT_FOUND"

    def __init__(
        self,
        error_code: Optional[str] = None,
        message: Optional[str] = None,
    ):
        super().__init__(error_code=error_code, message=message)


class AlreadyExists(ApiError):

    status_code = 409
    default_error_code = "CONFLICT"

    def __init__(
        self,
        error_code: Optional[str] = None,
        message: Optional[str] = None,
    ):
        super().__init__(error_code=error_code, message=message)


class Validation(ApiError):

    status_code = 422
    default_error_code = "VALIDATION_ERROR"

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(error_code=error_code, message=message)


class Unauthorized(ApiError):
    status_code = 401
    default_error_code = "UNAUTHORIZED"

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(error_code=error_code, message=message)


class Forbidden(ApiError):

    status_code = 403
    default_error_code = "FORBIDDEN"

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(error_code=error_code, message=message)
