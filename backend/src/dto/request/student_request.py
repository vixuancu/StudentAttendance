from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StudentCreateRequest(BaseModel):
    student_code: str = Field(..., min_length=1, max_length=100, description="Mã sinh viên")
    full_name: str = Field(..., min_length=1, max_length=100, description="Họ và tên")
    birth_of_date: Optional[datetime] = Field(None, description="Ngày sinh (ISO format, giờ VN)")
    gender: Optional[bool] = Field(None, description="Giới tính: false=Nữ, true=Nam")
    administrative_class_id: int = Field(..., ge=1, description="ID lớp hành chính")

    class Config:
        json_schema_extra = {
            "example": {
                "student_code": "22A1001D0043",
                "full_name": "Nguyễn Văn A",
                "birth_of_date": "2000-01-15T00:00:00",
                "gender": True,
                "administrative_class_id": 1,
            }
        }


class StudentUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    birth_of_date: Optional[datetime] = Field(None, description="Ngày sinh (ISO format, giờ VN)")
    gender: Optional[bool] = None
    administrative_class_id: Optional[int] = Field(None, ge=1)
    is_cancel: Optional[bool] = None
