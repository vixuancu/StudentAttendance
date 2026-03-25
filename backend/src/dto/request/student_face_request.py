from pydantic import BaseModel, Field


class StudentFaceCreateRequest(BaseModel):
    image_url: str = Field(..., min_length=1, description="Đường dẫn ảnh khuôn mặt")
    embedding: list[float] | None = Field(
        default=None,
        description="Embedding vector (tùy chọn, AI service sẽ cập nhật sau)",
    )
