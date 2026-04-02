from typing import Optional

from pydantic import BaseModel, Field


class CourseCreateRequest(BaseModel):
    course_name: str = Field(..., min_length=1, max_length=255)


class CourseUpdateRequest(BaseModel):
    course_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_cancel: Optional[bool] = None