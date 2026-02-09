from typing import Optional
from pydantic import BaseModel, Field

class StudentCreateRequest(BaseModel):
    student_code: str = Field(..., min_length=1, max_length=20, description="Mã sinh viên") # không để trống
    full_name: str = Field(..., min_length=1, max_length=100, description="Họ và tên")
    class_code: Optional[str] = Field(None, max_length=20, description="Mã lớp hành chính")
    email: Optional[str] = Field(None, max_length=100, description="email")
    phone: Optional[str] = Field(None, max_length=20, description="Số điện thoại")
    enrollment_year: Optional[int] = Field(None, ge=1900, le=2100, description="Năm nhập học")

    class Config:
        json_schema_extra = {
            "example": {
                "student_code": "2020CNTT001",
                "full_name": "Nguyễn Văn A",
                "class_code": "CNTT01",
                "email": "nguyenvana@hou.edu.vn",
                "phone": "0987654321",
                "enrollment_year": 2020
            }
        }

class StudentUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    class_code: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    enrollment_year: Optional[int] = Field(None, ge=2000, le=2100)
    status: Optional[str] = Field(None, description="ACTIVE, INACTIVE, GRADUATED, SUSPENDED")
