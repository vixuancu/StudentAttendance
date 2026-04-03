from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CourseResponse(BaseModel):
    id: int
    course_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
