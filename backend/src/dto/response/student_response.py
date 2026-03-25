from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StudentResponse(BaseModel):
    id: int
    student_code: str
    full_name: str
    birth_of_date: Optional[datetime] = None
    gender: Optional[bool] = None
    administrative_class_id: Optional[int] = None
    administrative_class_name: Optional[str] = None
    face_count: int = 0
    is_cancel: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdministrativeClassResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class StudentImportErrorResponse(BaseModel):
    row: int
    field: str
    student_code: Optional[str] = None
    message: str


class StudentImportResultResponse(BaseModel):
    total_rows: int
    imported_count: int
    failed_count: int
    errors: list[StudentImportErrorResponse] = []


class StudentStatsResponse(BaseModel):
    total: int
    active_count: int
    locked_count: int
