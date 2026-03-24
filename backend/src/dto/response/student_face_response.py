from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StudentFaceResponse(BaseModel):
    id: int
    student_id: int
    image_url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
