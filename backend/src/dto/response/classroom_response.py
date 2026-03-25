from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from src.dto.response.camera_response import CameraResponse


class ClassroomResponse(BaseModel):
    id: int
    class_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    camera: Optional[CameraResponse] = None

    class Config:
        from_attributes = True
