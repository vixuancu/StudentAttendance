from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CameraResponse(BaseModel):
    id: int
    camera_name: str
    ip_address: str
    camera_status: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
