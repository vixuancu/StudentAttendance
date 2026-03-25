from pydantic import BaseModel, Field


class AdministrativeClassCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Tên lớp hành chính")


class AdministrativeClassUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Tên lớp hành chính")
