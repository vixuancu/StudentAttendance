from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AccountResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    email: str
    gender: Optional[bool] = None
    birth_of_date: Optional[datetime] = None
    role_id: int
    role_name: Optional[str] = None
    is_cancel: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
