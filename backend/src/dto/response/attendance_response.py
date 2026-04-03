from datetime import datetime

from pydantic import BaseModel


class AIDemoConfigResponse(BaseModel):
    mode: str
    hidden_page_path: str
    rtsp_supported: bool
    debug_log_path: str | None = None


class AIDemoStartResponse(BaseModel):
    runtime_id: str
    mode: str
    started_at: float
    total_students: int
    cached_embeddings: int
    rtsp_url: str


class AIDemoStopResponse(BaseModel):
    stopped: bool
    total_attended: int


class AIDemoStatusResponse(BaseModel):
    active: bool
    runtime_id: str
    mode: str
    started_at: float | None = None
    total_attended: int
    cached_embeddings: int
    connected: bool


class AIDemoFaceResponse(BaseModel):
    recognized: bool
    student_id: int | None = None
    student_code: str | None = None
    full_name: str | None = None
    confidence: float | None = None
    already_marked: bool = False
    face_box: dict | None = None
    status: str | None = None
    confirm_hits: int | None = None
    confirm_required: int | None = None
    debug: dict | None = None


class AIDemoRecognizeResponse(BaseModel):
    status: str
    faces: list[AIDemoFaceResponse]
    total_faces: int
    new_attended: list[dict]
    total_attended: int
    elapsed_ms: float | None = None


class AIDemoFaceUploadResult(BaseModel):
    id: int
    image_url: str


class AIDemoFaceUploadResponse(BaseModel):
    uploaded: int
    failed: int
    faces: list[AIDemoFaceUploadResult]
    errors: list[str]
