import asyncio
import json
import time

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import StreamingResponse

from src.controller.attendance_controller import AttendanceController

from src.db.models.user import User
from src.deps import (
    get_ai_demo_runtime_service,
    get_attendance_controller,
)
from src.dto.common import DataResponse
from src.dto.request.attendance_request import AIDemoStartRequest, AIDemoStopRequest
from src.dto.response.attendance_response import (
    AIDemoConfigResponse,
    AIDemoFaceUploadResponse,
    AIDemoRecognizeResponse,
    AIDemoStartResponse,
    AIDemoStatusResponse,
    AIDemoStopResponse,
)
from src.middleware.auth import require_roles
from src.services.attendance_service import AIDemoService

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.get("/demo/config", response_model=DataResponse[AIDemoConfigResponse])
async def get_demo_config(ctrl: AttendanceController = Depends(get_attendance_controller)):
    return await ctrl.get_demo_config()


@router.post("/demo/start", response_model=DataResponse[AIDemoStartResponse])
async def start_demo(request: AIDemoStartRequest, ctrl: AttendanceController = Depends(get_attendance_controller)):
    return await ctrl.start_demo(mode=request.mode, rtsp_url=request.rtsp_url)


@router.post("/demo/stop", response_model=DataResponse[AIDemoStopResponse])
async def stop_demo(request: AIDemoStopRequest, ctrl: AttendanceController = Depends(get_attendance_controller)):
    return await ctrl.stop_demo(runtime_id=request.runtime_id)


@router.get("/demo/status", response_model=DataResponse[AIDemoStatusResponse])
async def get_demo_status(runtime_id: str | None = None, ctrl: AttendanceController = Depends(get_attendance_controller)):
    return await ctrl.get_demo_status(runtime_id=runtime_id)


@router.post("/demo/recognize-fast", response_model=DataResponse[AIDemoRecognizeResponse])
async def recognize_fast(
    runtime_id: str = Form(...),
    face_positions: str = Form("[]"),
    faces: list[UploadFile] = File(...),
    ctrl: AttendanceController = Depends(get_attendance_controller),
):
    return await ctrl.recognize_fast(runtime_id=runtime_id, faces=faces, face_positions=face_positions)


@router.post("/demo/students/{student_id}/faces/upload", response_model=DataResponse[AIDemoFaceUploadResponse])
async def upload_student_faces(
    student_id: int,
    files: list[UploadFile] = File(...),
    ctrl: AttendanceController = Depends(get_attendance_controller),
):
    return await ctrl.upload_student_faces(student_id=student_id, files=files)


@router.post("/live/start", response_model=DataResponse[AIDemoStartResponse])
async def start_live(
    request: AIDemoStartRequest,
    _current_user: User = Depends(require_roles("admin", "giao_vu", "giang_vien")),
    ctrl: AttendanceController = Depends(get_attendance_controller),
):
    return await ctrl.start_demo(mode=request.mode, rtsp_url=request.rtsp_url)


@router.post("/live/stop", response_model=DataResponse[AIDemoStopResponse])
async def stop_live(
    request: AIDemoStopRequest,
    _current_user: User = Depends(require_roles("admin", "giao_vu", "giang_vien")),
    ctrl: AttendanceController = Depends(get_attendance_controller),
):
    return await ctrl.stop_demo(runtime_id=request.runtime_id)


@router.get("/live/status", response_model=DataResponse[AIDemoStatusResponse])
async def get_live_status(
    runtime_id: str | None = None,
    _current_user: User = Depends(require_roles("admin", "giao_vu", "giang_vien")),
    ctrl: AttendanceController = Depends(get_attendance_controller),
):
    return await ctrl.get_demo_status(runtime_id=runtime_id)


@router.post("/live/recognize-fast", response_model=DataResponse[AIDemoRecognizeResponse])
async def recognize_fast_live(
    runtime_id: str = Form(...),
    face_positions: str = Form("[]"),
    faces: list[UploadFile] = File(...),
    _current_user: User = Depends(require_roles("admin", "giao_vu", "giang_vien")),
    ctrl: AttendanceController = Depends(get_attendance_controller),
):
    return await ctrl.recognize_fast(runtime_id=runtime_id, faces=faces, face_positions=face_positions)


async def _mjpeg_generator(runtime_id: str, service: AIDemoService):
    delay = 1.0 / 15.0
    last_seq = -1
    while True:
        if not service.is_runtime_active(runtime_id):
            break
        packet = service.get_stream_packet(runtime_id)
        if packet is None:
            await asyncio.sleep(delay)
            continue
        seq, frame_bytes = packet
        if frame_bytes and seq != last_seq:
            last_seq = seq
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
        await asyncio.sleep(delay)


@router.get("/demo/ip/stream/{runtime_id}")
async def demo_ip_stream(runtime_id: str, service: AIDemoService = Depends(get_ai_demo_runtime_service)):
    return StreamingResponse(
        _mjpeg_generator(runtime_id=runtime_id, service=service),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


async def _sse_generator(request: Request, runtime_id: str, service: AIDemoService):
    last_processed = -1
    last_heartbeat = time.time()
    while True:
        if await request.is_disconnected():
            break
        if not service.is_runtime_active(runtime_id):
            break

        payload = service.get_results_payload(runtime_id)
        if payload:
            processed = int(payload.get("processed_count", 0))
            if processed > last_processed:
                last_processed = processed
                data = json.dumps(payload)
                yield f"data: {data}\n\n"

        now = time.time()
        if now - last_heartbeat > 5.0:
            yield ": heartbeat\n\n"
            last_heartbeat = now

        await asyncio.sleep(0.1)


@router.get("/demo/ip/results/{runtime_id}")
async def demo_ip_results(request: Request, runtime_id: str, service: AIDemoService = Depends(get_ai_demo_runtime_service)):
    return StreamingResponse(
        _sse_generator(request=request, runtime_id=runtime_id, service=service),
        media_type="text/event-stream",
    )

