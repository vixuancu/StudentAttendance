from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CameraCreateRequest(BaseModel):
    camera_name: str = Field(..., min_length=1, max_length=255)
    ip_address: str = Field(..., min_length=3, max_length=39)
    camera_status: int = Field(default=0, ge=0, le=1)
    classroom_id: int = Field(...)

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        import ipaddress

        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError("Định dạng IP không hợp lệ")
        return v


class CameraUpdateRequest(BaseModel):
    camera_name: Optional[str] = Field(None, min_length=1, max_length=255)
    ip_address: Optional[str] = Field(None, min_length=3, max_length=39)
    camera_status: Optional[int] = Field(None, ge=0, le=1)
    classroom_id: Optional[int] = Field(None)

    @field_validator("ip_address")
    @classmethod
    def validate_ip_update(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        import ipaddress

        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError("Định dạng IP không hợp lệ")
        return v
