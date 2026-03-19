from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StudentResponse(BaseModel):
    id: int
    full_name: str
    birth_of_date: Optional[datetime] = None
    gender: Optional[bool] = None
    administrative_class: str
    is_cancel: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
