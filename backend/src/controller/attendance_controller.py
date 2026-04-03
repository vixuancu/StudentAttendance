from src.dto.common import DataResponse
from src.dto.response.attendance_response import (
    AIDemoConfigResponse,
    AIDemoFaceUploadResponse,
    AIDemoRecognizeResponse,
    AIDemoStartResponse,
    AIDemoStatusResponse,
    AIDemoStopResponse,
)
from src.services.attendance_service import AIDemoService


class AttendanceController:
    def __init__(self, service: AIDemoService):
        self.service = service

    async def get_demo_config(self) -> DataResponse[AIDemoConfigResponse]:
        data = await self.service.get_config()
        return DataResponse(
            data=AIDemoConfigResponse.model_validate(data),
            message="Lấy cấu hình demo AI thành công",
        )

    async def start_demo(self, mode: str, rtsp_url: str | None) -> DataResponse[AIDemoStartResponse]:
        data = await self.service.start(mode=mode, rtsp_url=rtsp_url)
        return DataResponse(
            data=AIDemoStartResponse.model_validate(data),
            message="Khởi động demo AI thành công",
        )

    async def stop_demo(self, runtime_id: str | None) -> DataResponse[AIDemoStopResponse]:
        data = await self.service.stop(runtime_id=runtime_id)
        return DataResponse(
            data=AIDemoStopResponse.model_validate(data),
            message="Dừng demo AI thành công",
        )

    async def get_demo_status(self, runtime_id: str | None) -> DataResponse[AIDemoStatusResponse]:
        data = await self.service.status(runtime_id=runtime_id)
        return DataResponse(
            data=AIDemoStatusResponse.model_validate(data),
            message="Lấy trạng thái demo AI thành công",
        )

    async def recognize_fast(self, runtime_id: str, faces, face_positions: str) -> DataResponse[AIDemoRecognizeResponse]:
        data = await self.service.recognize_fast(
            runtime_id=runtime_id,
            face_files=faces,
            face_positions_json=face_positions,
        )
        return DataResponse(
            data=AIDemoRecognizeResponse.model_validate(data),
            message="Nhận diện nhanh thành công",
        )

    async def get_runtime_stream_packet(self, runtime_id: str):
        return self.service.get_stream_packet(runtime_id)

    async def get_runtime_results_payload(self, runtime_id: str):
        return self.service.get_results_payload(runtime_id)

    async def is_runtime_active(self, runtime_id: str) -> bool:
        return self.service.is_runtime_active(runtime_id)

    async def upload_student_faces(self, student_id: int, files) -> DataResponse[AIDemoFaceUploadResponse]:
        data = await self.service.upload_student_faces(student_id=student_id, files=files)
        return DataResponse(
            data=AIDemoFaceUploadResponse.model_validate(data),
            message="Upload khuôn mặt thành công",
        )
