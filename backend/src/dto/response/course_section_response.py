from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CourseSectionResponse(BaseModel):
    id: int
    name: str
    course_id: int
    course_name: str
    user_id: int
    user_full_name: Optional[str] = None
    room_id: int
    room_name: str
    day_of_week: int
    start_date: datetime
    end_date: datetime
    start_period: int
    number_of_periods: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    hoc_ky: str
    si_so: int
    is_cancel: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourseSectionOptionResponse(BaseModel):
    id: int
    name: str


class CourseSectionFormOptionsResponse(BaseModel):
    courses: list[CourseSectionOptionResponse]
    lecturers: list[CourseSectionOptionResponse]
    rooms: list[CourseSectionOptionResponse]
