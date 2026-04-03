from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class CourseSectionCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    course_id: int = Field(..., ge=1)
    user_id: int = Field(..., ge=1)
    room_id: int = Field(..., ge=1)
    day_of_week: int = Field(..., ge=2, le=8)
    start_date: datetime
    end_date: datetime
    start_period: int = Field(..., ge=1)
    number_of_periods: int = Field(..., ge=1)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")

        return self


class CourseSectionUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    course_id: Optional[int] = Field(None, ge=1)
    user_id: Optional[int] = Field(None, ge=1)
    room_id: Optional[int] = Field(None, ge=1)
    day_of_week: Optional[int] = Field(None, ge=2, le=8)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    start_period: Optional[int] = Field(None, ge=1)
    number_of_periods: Optional[int] = Field(None, ge=1)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_cancel: Optional[bool] = None

    @model_validator(mode="after")
    def validate_time_range(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date >= self.end_date
        ):
            raise ValueError("start_date must be before end_date")

        if (
            self.start_time is not None
            and self.end_time is not None
            and self.start_time >= self.end_time
        ):
            raise ValueError("start_time must be before end_time")

        return self
