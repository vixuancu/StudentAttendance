from pydantic import BaseModel, Field, field_validator


class AIDemoStartRequest(BaseModel):
    mode: str = Field(default="webcam", description="webcam | ip_camera | both")
    rtsp_url: str | None = Field(default=None, description="RTSP URL nếu dùng IP camera")

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        normalized = (value or "").strip().lower()
        if normalized not in {"webcam", "ip_camera", "both"}:
            raise ValueError("mode phải là webcam, ip_camera hoặc both")
        return normalized


class AIDemoStopRequest(BaseModel):
    runtime_id: str | None = None


class AIDemoRecognizeFastRequest(BaseModel):
    runtime_id: str = Field(..., min_length=1)
    face_positions: str = Field(default="[]")
