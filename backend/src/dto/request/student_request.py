from typing import Optional
from pydantic import BaseModel, Field


class StudentCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100, description="Họ và tên")
    birth_of_date: Optional[str] = Field(None, description="Ngày sinh (ISO format)")
    gender: Optional[int] = Field(None, ge=0, le=2, description="Giới tính: 0=Nữ, 1=Nam, 2=Khác")
    administrative_class: str = Field(..., min_length=1, max_length=100, description="Lớp hành chính")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Nguyễn Văn A",
                "birth_of_date": "2000-01-15T00:00:00",
                "gender": 1,
                "administrative_class": "CNTT01"
            }
        }


class StudentUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    birth_of_date: Optional[str] = Field(None, description="Ngày sinh (ISO format)")
    gender: Optional[int] = Field(None, ge=0, le=2)
    administrative_class: Optional[str] = Field(None, min_length=1, max_length=100)
