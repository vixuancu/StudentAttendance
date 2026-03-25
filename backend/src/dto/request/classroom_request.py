from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ClassroomCreateRequest(BaseModel):
    class_name: str = Field(..., min_length=1, max_length=255)


class ClassroomUpdateRequest(BaseModel):
    class_name: Optional[str] = Field(None, min_length=1, max_length=255)
