"""
Business exceptions - dùng trong Service layer.
KHÔNG phụ thuộc vào HTTP/FastAPI.
"""


class BusinessException(Exception):
    """Base exception cho tất cả business errors"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class NotFoundException(BusinessException):
    """Resource không tồn tại"""
    
    def __init__(self, resource: str, identifier: str | int):
        message = f"{resource} với ID '{identifier}' không tồn tại"
        super().__init__(message, error_code="NOT_FOUND")
        self.resource = resource
        self.identifier = identifier


class AlreadyExistsException(BusinessException):
    """Resource đã tồn tại"""
    
    def __init__(self, resource: str, field: str, value: str):
        message = f"{resource} với {field} '{value}' đã tồn tại"
        super().__init__(message, error_code="ALREADY_EXISTS")
        self.resource = resource
        self.field = field
        self.value = value


class ValidationException(BusinessException):
    """Lỗi validation business logic"""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message, error_code="VALIDATION_ERROR")
        self.field = field
