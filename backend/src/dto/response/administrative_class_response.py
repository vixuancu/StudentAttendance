from datetime import datetime
from pydantic import BaseModel


class AdministrativeClassItemResponse(BaseModel):
    id: int
    name: str
    student_count: int = 0
    is_cancel: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class AdministrativeClassStatsResponse(BaseModel):
    total: int
    active_count: int
    locked_count: int
