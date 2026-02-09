from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class StudentResponse(BaseModel):
    id: int 
    student_code: str
    full_name: str
    class_code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    enrollment_year: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # cho phéo convert từ SQLAlchemy model
