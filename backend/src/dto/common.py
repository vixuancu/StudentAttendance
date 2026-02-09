from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class BaseResponse(BaseModel):
    """
    Base response wrapper 
    """
    success: bool = True
    message: str = "Success"

class DataResponse(BaseResponse, Generic[T]):
    """
    Response with single data
    """
    data: Optional[T] = None 

class ListResponse(BaseResponse, Generic[T]):
    """Response with list data + pagination"""
    data: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0

class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None # kiểu dict để lưu trữ thông tin chi tiết về lỗi

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    page_size: int = 10

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size
