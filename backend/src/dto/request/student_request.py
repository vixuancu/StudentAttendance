from typing import Optional
from pydantic import BaseModel, Field


class StudentCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100, description="Họ và tên")
    birth_of_date: Optional[str] = Field(None, description="Ngày sinh (ISO format)")
    gender: Optional[bool] = Field(None, description="Giới tính: false=Nữ, true=Nam")
    administrative_class: str = Field(..., min_length=1, max_length=100, description="Lớp hành chính")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Nguyễn Văn A",
                "birth_of_date": "2000-01-15T00:00:00",
                "gender": True,
                "administrative_class": "CNTT01"
            }
        }


class StudentUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    birth_of_date: Optional[str] = Field(None, description="Ngày sinh (ISO format)")
    gender: Optional[bool] = None
    administrative_class: Optional[str] = Field(None, min_length=1, max_length=100)
