from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CameraDetailResponse(BaseModel):
    id: int
    camera_name: str
    ip_address: str
    camera_status: int
    classroom_id: Optional[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CameraResponse(BaseModel):
    id: int = Field(..., serialization_alias="camera_id")
    camera_name: str
    ip_address: str

    model_config = {"from_attributes": True, "populate_by_name": True}
