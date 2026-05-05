import asyncio
from datetime import datetime
import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from src.config.settings import settings
from src.db.models.enums import AttendanceStatus, SessionStatus
from src.db.models.user import User
from src.repository.ai_demo_repo import AIDemoRepository
from src.services.recognition_service import (
    AIDemoRTSPWorker,
    build_cache_from_rows,
    extract_embedding_from_path,
    extract_embeddings_from_crops,
    match_from_cache,
)
from src.services.antispoof_service import check_liveness
from src.utils.ai_demo_logger import get_ai_demo_log_path, log_ai_demo_event
from src.utils.exceptions import ForbiddenException, ValidationException


_backend_dir = Path(__file__).resolve().parents[2]
(_backend_dir / "uploads").mkdir(parents=True, exist_ok=True)


@dataclass
class AIDemoRuntime:
    lock: threading.RLock = field(default_factory=threading.RLock)
    active: bool = False
    runtime_id: str = ""
    mode: str = "webcam"
    started_at: float = 0.0
    rtsp_url: str = ""
    class_session_id: Optional[int] = None
    course_section_id: Optional[int] = None
    course_section_name: str = ""
    course_name: str = ""
    lecturer_id: Optional[int] = None
    lecturer_name: str = ""
    room_id: Optional[int] = None
    room_name: str = ""
    session_date: Optional[object] = None
    start_time: Optional[object] = None
    end_time: Optional[object] = None
    late_time: Optional[object] = None
    cache_data: dict = field(default_factory=lambda: build_cache_from_rows([]))
    attended_student_ids: set[int] = field(default_factory=set)
    enrolled_student_ids: set[int] = field(default_factory=set)
    owner_user_id: Optional[int] = None
    worker: Optional[AIDemoRTSPWorker] = None

    def reset(self):
        self.active = False
        self.runtime_id = ""
        self.mode = "webcam"
        self.started_at = 0.0
        self.rtsp_url = ""
        self.class_session_id = None
        self.course_section_id = None
        self.course_section_name = ""
        self.course_name = ""
        self.lecturer_id = None
        self.lecturer_name = ""
        self.room_id = None
        self.room_name = ""
        self.session_date = None
        self.start_time = None
        self.end_time = None
        self.late_time = None
        self.attended_student_ids.clear()
        self.enrolled_student_ids.clear()
        self.owner_user_id = None
        self.cache_data = build_cache_from_rows([])
        if self.worker:
            self.worker.stop()
        self.worker = None


_RUNTIME = AIDemoRuntime()


def get_ai_demo_runtime() -> AIDemoRuntime:
    return _RUNTIME


class AIDemoService:
    def __init__(self, repo: AIDemoRepository | None, runtime: AIDemoRuntime):
        self.repo = repo
        self.runtime = runtime

    @staticmethod
    def _extract_role_name(user: User) -> str | None:
        role = user.__dict__.get("role")
        return role.role_name if role else None

    def _build_start_payload(self, cache_info: dict) -> dict:
        return {
            "runtime_id": self.runtime.runtime_id,
            "mode": self.runtime.mode,
            "started_at": self.runtime.started_at,
            "total_students": cache_info["students"],
            "cached_embeddings": cache_info["embeddings"],
            "rtsp_url": self.runtime.rtsp_url,
            "class_session_id": self.runtime.class_session_id,
            "course_section_id": self.runtime.course_section_id,
            "course_section_name": self.runtime.course_section_name,
            "course_name": self.runtime.course_name,
            "lecturer_id": self.runtime.lecturer_id,
            "lecturer_name": self.runtime.lecturer_name,
            "room_id": self.runtime.room_id,
            "room_name": self.runtime.room_name,
            "session_date": self.runtime.session_date,
            "start_time": self.runtime.start_time,
            "end_time": self.runtime.end_time,
        }

    def _build_status_payload(self, connected: bool) -> dict:
        return {
            "active": True,
            "runtime_id": self.runtime.runtime_id,
            "mode": self.runtime.mode,
            "started_at": self.runtime.started_at,
            "total_attended": len(self.runtime.attended_student_ids),
            "cached_embeddings": int(self.runtime.cache_data["n_embeddings"]),
            "connected": connected,
            "class_session_id": self.runtime.class_session_id,
            "course_section_id": self.runtime.course_section_id,
            "course_section_name": self.runtime.course_section_name,
            "course_name": self.runtime.course_name,
            "lecturer_id": self.runtime.lecturer_id,
            "lecturer_name": self.runtime.lecturer_name,
            "room_id": self.runtime.room_id,
            "room_name": self.runtime.room_name,
            "session_date": self.runtime.session_date,
            "start_time": self.runtime.start_time,
            "end_time": self.runtime.end_time,
        }

    @staticmethod
    def _resolve_attendance_status(late_time: Optional[object], start_time: Optional[object] = None) -> int:
        target_time = late_time
        if not isinstance(target_time, datetime):
            if isinstance(start_time, datetime):
                from datetime import timedelta
                target_time = start_time + timedelta(minutes=15)
            else:
                return AttendanceStatus.PRESENT

        now = datetime.now(tz=target_time.tzinfo) if target_time.tzinfo else datetime.now()
        if now > target_time:
            return AttendanceStatus.LATE
        return AttendanceStatus.PRESENT

    async def _upsert_attendance(self, student_id: int, class_session_id: int, status: int) -> None:
        if self.repo is None:
            return

        existing = await self.repo.get_attendance_by_student_and_session(
            student_id=student_id,
            class_session_id=class_session_id,
            include_cancel=True,
        )
        if existing is None:
            await self.repo.create_attendance(
                student_id=student_id,
                class_session_id=class_session_id,
                status=status,
                note=None,
            )
            return

        if existing.status == AttendanceStatus.PRESENT and status == AttendanceStatus.LATE:
            return

        await self.repo.update_attendance(attendance=existing, status=status, note=None)

    async def get_config(self) -> dict:
        return {
            "mode": settings.ai_demo_mode,
            "hidden_page_path": settings.ai_demo_hidden_page_path,
            "rtsp_supported": True,
            "debug_log_path": get_ai_demo_log_path(),
        }

    async def rebuild_cache(self) -> dict:
        if self.repo is None:
            raise ValidationException("Repository chưa được khởi tạo", field="repo")
        rows = await self.repo.fetch_active_student_faces()
        cache_data = build_cache_from_rows(rows)
        with self.runtime.lock:
            self.runtime.cache_data = cache_data
        log_ai_demo_event(
            "cache_rebuild",
            students=cache_data["n_students"],
            embeddings=cache_data["n_embeddings"],
        )
        return {
            "students": cache_data["n_students"],
            "embeddings": cache_data["n_embeddings"],
        }

    def _normalize_mode(self, requested_mode: Optional[str]) -> str:
        allowed = {"webcam", "ip_camera", "both"}
        mode = (requested_mode or settings.ai_demo_mode or "webcam").strip().lower()
        if mode not in allowed:
            raise ValidationException("Mode không hợp lệ", field="mode")

        env_mode = settings.ai_demo_mode.strip().lower()
        if env_mode not in allowed:
            env_mode = "both"

        if env_mode == "both":
            if mode == "both":
                return "webcam"
            return mode

        if mode == "both":
            return env_mode

        if mode != env_mode:
            raise ValidationException(
                f"Mode hiện tại chỉ cho phép '{env_mode}'",
                field="mode",
            )
        return mode

    async def start(self, mode: Optional[str], rtsp_url: Optional[str]) -> dict:
        selected_mode = self._normalize_mode(mode)
        cache_info = await self.rebuild_cache()
        if cache_info["embeddings"] == 0:
            raise ValidationException(
                "Không có embedding nào trong student_faces. Hãy upload ảnh sinh viên trước.",
                field="cache",
            )

        cleaned_rtsp = (rtsp_url or "").strip().replace(" ", "")
        if selected_mode == "ip_camera":
            if not cleaned_rtsp:
                raise ValidationException("RTSP URL không được để trống", field="rtsp_url")
            if not cleaned_rtsp.lower().startswith(("rtsp://", "rtsps://")):
                raise ValidationException("RTSP URL phải bắt đầu bằng rtsp:// hoặc rtsps://", field="rtsp_url")

        with self.runtime.lock:
            if self.runtime.worker:
                self.runtime.worker.stop()
                self.runtime.worker = None

            self.runtime.active = True
            self.runtime.runtime_id = uuid.uuid4().hex
            self.runtime.mode = selected_mode
            self.runtime.started_at = time.time()
            self.runtime.rtsp_url = cleaned_rtsp
            self.runtime.class_session_id = None
            self.runtime.course_section_id = None
            self.runtime.course_section_name = ""
            self.runtime.course_name = ""
            self.runtime.lecturer_id = None
            self.runtime.lecturer_name = ""
            self.runtime.room_id = None
            self.runtime.room_name = ""
            self.runtime.session_date = None
            self.runtime.start_time = None
            self.runtime.end_time = None
            self.runtime.late_time = None
            self.runtime.attended_student_ids.clear()
            self.runtime.enrolled_student_ids.clear()
            self.runtime.owner_user_id = None

            if selected_mode == "ip_camera":
                worker = AIDemoRTSPWorker(
                    rtsp_url=cleaned_rtsp,
                    get_cache=self._get_cache,
                    is_attended=self._is_attended,
                    mark_attended=self._mark_attended,
                    runtime_id=self.runtime.runtime_id,
                )
                worker.start()
                self.runtime.worker = worker

            log_ai_demo_event(
                "runtime_start",
                runtime_id=self.runtime.runtime_id,
                mode=self.runtime.mode,
                rtsp_url=self.runtime.rtsp_url,
                cached_embeddings=cache_info["embeddings"],
            )

            return self._build_start_payload(cache_info)

    async def start_live(
        self,
        mode: Optional[str],
        class_session_id: int,
        course_section_id: int,
        current_user: User,
    ) -> dict:
        if self.repo is None:
            raise ValidationException("Repository chưa được khởi tạo", field="repo")

        selected_mode = (mode or "webcam").strip().lower()
        if selected_mode != "webcam":
            raise ValidationException("live attendance hiện chỉ hỗ trợ mode webcam", field="mode")

        session = await self.repo.get_class_session_detail(class_session_id)
        if session is None:
            raise ValidationException("Buổi học không tồn tại hoặc đã bị hủy", field="class_session_id")

        course_section = session.course_section
        if course_section is None or course_section.is_cancel:
            raise ValidationException("Lớp tín chỉ của buổi học không hợp lệ", field="class_session_id")

        if int(course_section.id) != int(course_section_id):
            raise ValidationException(
                "Buổi học không thuộc lớp tín chỉ đã chọn",
                field="course_section_id",
            )

        if session.status == SessionStatus.CANCELLED:
            raise ValidationException("Buổi học đã được đánh dấu nghỉ, không thể mở điểm danh", field="class_session_id")

        if session.session_date and session.start_time:
            now = datetime.now()
            
            if isinstance(session.start_time, datetime):
                session_start_datetime = session.start_time
            else:
                session_start_datetime = datetime.combine(session.session_date.date(), session.start_time)
                
            if session.end_time:
                if isinstance(session.end_time, datetime):
                    session_end_datetime = session.end_time
                else:
                    session_end_datetime = datetime.combine(session.session_date.date(), session.end_time)
                    if session_end_datetime < session_start_datetime:
                        from datetime import timedelta
                        session_end_datetime += timedelta(days=1)
                
                if now > session_end_datetime:
                    raise ValidationException("Ca học đã kết thúc, không thể mở điểm danh.", field="time")
            
            time_diff = (session_start_datetime - now).total_seconds()
            
            # Check if attempting to start more than 15 minutes before class
            if time_diff > 15 * 60:
                # raise ValidationException("Chưa đến giờ học. Chỉ có thể mở điểm danh tối đa trước 15 phút.", field="time")
                raise ValidationException("Không đúng buổi học..", field="time")
            
            # Nếu đã qua các check trên (tức là không mở trước quá 15p và chưa kết thúc)
            # thì ta không cần check session_date == now.date() một cách cứng nhắc 
            # vì có thể ca học kết thúc qua ngày hôm sau 

        role_name = self._extract_role_name(current_user)
        if role_name == "giang_vien" and int(course_section.user_id) != int(current_user.id):
            raise ForbiddenException("Giảng viên chỉ được mở điểm danh cho buổi học thuộc lớp mình quản lý")

        enrolled_students = await self.repo.count_active_enrollments_by_course_section(int(course_section.id))
        if enrolled_students <= 0:
            raise ValidationException(
                "Lớp tín chỉ này chưa có sinh viên đăng ký nên không thể mở điểm danh",
                field="enrollment",
            )

        rows = await self.repo.fetch_student_faces_by_course_section(int(course_section.id))
        enrolled_student_ids = await self.repo.fetch_enrolled_student_ids_by_course_section(int(course_section.id))
        cache_data = build_cache_from_rows(rows)
        if cache_data["n_embeddings"] == 0:
            raise ValidationException(
                "Lớp tín chỉ này chưa có dữ liệu khuôn mặt sinh viên để điểm danh",
                field="cache",
            )

        cache_info = {
            "students": int(enrolled_students),
            "embeddings": cache_data["n_embeddings"],
        }

        with self.runtime.lock:
            if (
                self.runtime.active
                and self.runtime.class_session_id is not None
                and self.runtime.owner_user_id is not None
                and int(self.runtime.owner_user_id) != int(current_user.id)
            ):
                raise ForbiddenException("Đang có phiên điểm danh live do người dùng khác vận hành")

            if self.runtime.worker:
                self.runtime.worker.stop()
                self.runtime.worker = None

            self.runtime.active = True
            self.runtime.runtime_id = uuid.uuid4().hex
            self.runtime.mode = selected_mode
            self.runtime.started_at = time.time()
            self.runtime.rtsp_url = ""
            self.runtime.class_session_id = int(session.id)
            self.runtime.course_section_id = int(course_section.id)
            self.runtime.course_section_name = course_section.name or ""
            self.runtime.course_name = course_section.course.course_name if course_section.course else ""
            self.runtime.lecturer_id = int(course_section.user_id)
            self.runtime.lecturer_name = course_section.user.full_name if course_section.user else ""
            room = session.room if session.room else course_section.room
            self.runtime.room_id = int(room.id) if room else None
            self.runtime.room_name = room.class_name if room else ""
            self.runtime.session_date = session.session_date
            self.runtime.start_time = session.start_time
            self.runtime.end_time = session.end_time
            self.runtime.late_time = session.late_time
            
            attended_students = await self.repo.get_attended_student_ids_by_session(int(session.id))

            self.runtime.cache_data = cache_data
            self.runtime.enrolled_student_ids = set(enrolled_student_ids)
            self.runtime.attended_student_ids = attended_students
            self.runtime.owner_user_id = int(current_user.id)

            log_ai_demo_event(
                "runtime_start_live",
                runtime_id=self.runtime.runtime_id,
                mode=self.runtime.mode,
                class_session_id=self.runtime.class_session_id,
                course_section_id=self.runtime.course_section_id,
                lecturer_id=self.runtime.lecturer_id,
                cached_embeddings=cache_info["embeddings"],
            )

            return self._build_start_payload(cache_info)

    def _ensure_live_runtime_owner(self, current_user: User) -> None:
        with self.runtime.lock:
            if not self.runtime.active:
                return
            if self.runtime.class_session_id is None:
                raise ValidationException("Runtime hiện tại không phải phiên điểm danh live", field="runtime")
            owner_user_id = self.runtime.owner_user_id

        if owner_user_id is None:
            return
        if int(owner_user_id) != int(current_user.id):
            raise ForbiddenException("Bạn không có quyền thao tác trên phiên điểm danh này")

    async def stop(self, runtime_id: Optional[str]) -> dict:
        with self.runtime.lock:
            if not self.runtime.active:
                return {
                    "stopped": True,
                    "total_attended": 0,
                }

            if runtime_id and runtime_id != self.runtime.runtime_id:
                raise ValidationException("runtime_id không hợp lệ", field="runtime_id")

            total = len(self.runtime.attended_student_ids)
            old_runtime = self.runtime.runtime_id
            self.runtime.reset()
            log_ai_demo_event(
                "runtime_stop",
                runtime_id=old_runtime,
                total_attended=total,
            )
            return {
                "stopped": True,
                "total_attended": total,
            }

    async def stop_live(self, runtime_id: Optional[str], current_user: User) -> dict:
        self._ensure_live_runtime_owner(current_user)

        absent_ids = []
        class_session_id = None

        with self.runtime.lock:
            if self.runtime.active and self.runtime.class_session_id is not None:
                if not runtime_id or runtime_id == self.runtime.runtime_id:
                    class_session_id = self.runtime.class_session_id
                    enrolled = self.runtime.enrolled_student_ids
                    attended = self.runtime.attended_student_ids
                    absent_ids = list(set(enrolled) - attended)

        if class_session_id is not None:
            for sid in absent_ids:
                await self._upsert_attendance(
                    student_id=sid,
                    class_session_id=class_session_id,
                    status=AttendanceStatus.ABSENT,
                )

        return await self.stop(runtime_id=runtime_id)

    async def status(self, runtime_id: Optional[str]) -> dict:
        with self.runtime.lock:
            if not self.runtime.active:
                return {
                    "active": False,
                    "runtime_id": "",
                    "mode": "",
                    "total_attended": 0,
                    "cached_embeddings": int(self.runtime.cache_data["n_embeddings"]),
                    "connected": False,
                }

            if runtime_id and runtime_id != self.runtime.runtime_id:
                raise ValidationException("runtime_id không hợp lệ", field="runtime_id")

            connected = self.runtime.worker.connected if self.runtime.worker else True
            return self._build_status_payload(connected)

    async def status_live(self, runtime_id: Optional[str], current_user: User) -> dict:
        self._ensure_live_runtime_owner(current_user)
        return await self.status(runtime_id=runtime_id)

    async def recognize_fast(self, runtime_id: str, face_files, face_positions_json: str) -> dict:
        with self.runtime.lock:
            if not self.runtime.active:
                raise ValidationException("Demo chưa start", field="runtime")
            if runtime_id != self.runtime.runtime_id:
                raise ValidationException("runtime_id không hợp lệ", field="runtime_id")
            if self.runtime.mode not in {"webcam", "both"}:
                raise ValidationException("Runtime hiện tại không ở chế độ webcam", field="mode")
            cache_data = self.runtime.cache_data
            class_session_id = self.runtime.class_session_id
            late_time = self.runtime.late_time
            start_time = self.runtime.start_time
            enrolled_student_ids = set(self.runtime.enrolled_student_ids)

        if settings.ai_demo_debug_log_verbose:
            log_ai_demo_event(
                "webcam_recognize_call",
                runtime_id=runtime_id,
                positions_payload_size=len(face_positions_json or ""),
                files_count=len(face_files),
            )

        t0 = time.perf_counter()
        try:
            positions = json.loads(face_positions_json or "[]")
        except (json.JSONDecodeError, TypeError):
            positions = []

        crops = []
        for ff in face_files:
            content = await ff.read()
            if not content:
                continue
            arr = np.frombuffer(content, np.uint8)
            crop = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if crop is not None:
                crops.append(crop)

        if settings.ai_demo_debug_log_verbose:
            log_ai_demo_event(
                "webcam_recognize_input",
                runtime_id=runtime_id,
                uploaded_faces=len(face_files),
                decoded_crops=len(crops),
                positions_count=len(positions),
            )

        if not crops:
            with self.runtime.lock:
                total_attended_now = len(self.runtime.attended_student_ids)
            return {
                "status": "no_face",
                "faces": [],
                "total_faces": 0,
                "new_attended": [],
                "total_attended": total_attended_now,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
            }

        embeddings_with_quality = await asyncio.to_thread(extract_embeddings_from_crops, crops)

        # Liveness check map
        liveness_results = await asyncio.to_thread(lambda c_list: [check_liveness(c) for c in c_list], crops)

        results = []
        new_attended = []
        debug_faces = []
        emb_ok_count = 0
        for i, (emb, quality) in enumerate(embeddings_with_quality):
            pos = positions[i] if i < len(positions) and isinstance(positions[i], dict) else {}
            face_box = {
                "xCenter": float(pos.get("xCenter", 0.0)),
                "yCenter": float(pos.get("yCenter", 0.0)),
            }

            is_real, liveness_score = liveness_results[i]
            
            if not is_real:
                # Spoof detected
                results.append({
                    "recognized": False, 
                    "is_spoof": True,
                    "liveness_score": liveness_score,
                    "face_box": face_box, 
                    "debug": {"reason": "spoof_detected"}
                })
                debug_faces.append({"idx": i, "reason": "spoof_detected", "liveness": liveness_score})
                continue

            if emb is None:
                results.append({"recognized": False, "face_box": face_box, "debug": {"reason": "no_embedding"}})
                debug_faces.append({"idx": i, "reason": "no_embedding", "quality": round(float(quality), 4)})
                continue

            emb_ok_count += 1

            match, score, dbg = match_from_cache(emb, cache_data, float(quality))
            if match is None:
                results.append({"recognized": False, "face_box": face_box, "debug": dbg})
                debug_faces.append({
                    "idx": i,
                    "reason": dbg.get("reason", "unmatched"),
                    "quality": round(float(quality), 4),
                    "best": dbg.get("best"),
                    "threshold": dbg.get("threshold"),
                    "margin": dbg.get("margin"),
                })
                continue

            sid = int(match["student_id"])
            if class_session_id is not None and sid not in enrolled_student_ids:
                not_enrolled_debug = {
                    **dbg,
                    "reason": "not_enrolled_in_session",
                }
                results.append(
                    {
                        "recognized": False,
                        "face_box": face_box,
                        "debug": not_enrolled_debug,
                    }
                )
                debug_faces.append(
                    {
                        "idx": i,
                        "reason": "not_enrolled_in_session",
                        "student_id": sid,
                        "quality": round(float(quality), 4),
                        "best": dbg.get("best"),
                        "threshold": dbg.get("threshold"),
                        "margin": dbg.get("margin"),
                    }
                )
                continue

            with self.runtime.lock:
                already = sid in self.runtime.attended_student_ids
                if not already:
                    self.runtime.attended_student_ids.add(sid)

            if not already and class_session_id is not None:
                attendance_status = self._resolve_attendance_status(late_time, start_time)
                await self._upsert_attendance(
                    student_id=sid,
                    class_session_id=class_session_id,
                    status=attendance_status,
                )

            if not already:
                new_attended.append(
                    {
                        "student_id": sid,
                        "student_code": match["student_code"],
                        "full_name": match["full_name"],
                        "confidence": round(float(score) * 100, 1),
                    }
                )

            results.append(
                {
                    "recognized": True,
                    "is_spoof": False,
                    "liveness_score": liveness_score,
                    "student_id": sid,
                    "student_code": match["student_code"],
                    "full_name": match["full_name"],
                    "confidence": round(float(score) * 100, 1),
                    "already_marked": already,
                    "face_box": face_box,
                    "debug": dbg,
                }
            )
            debug_faces.append(
                {
                    "idx": i,
                    "reason": "matched",
                    "student_id": sid,
                    "quality": round(float(quality), 4),
                    "best": dbg.get("best"),
                    "threshold": dbg.get("threshold"),
                    "margin": dbg.get("margin"),
                }
            )

        elapsed = round((time.perf_counter() - t0) * 1000, 1)
        with self.runtime.lock:
            total_attended = len(self.runtime.attended_student_ids)

        recognized_count = len([f for f in results if f.get("recognized")])
        if settings.ai_demo_debug_log_verbose:
            log_ai_demo_event(
                "webcam_recognize_result",
                runtime_id=runtime_id,
                crops_count=len(crops),
                emb_ok_count=emb_ok_count,
                recognized_count=recognized_count,
                new_attended_count=len(new_attended),
                total_attended=total_attended,
                elapsed_ms=elapsed,
                faces_debug=debug_faces,
            )

        return {
            "status": "success",
            "faces": results,
            "total_faces": len(results),
            "new_attended": new_attended,
            "total_attended": total_attended,
            "elapsed_ms": elapsed,
        }

    async def recognize_fast_live(
        self,
        runtime_id: str,
        face_files,
        face_positions_json: str,
        current_user: User,
    ) -> dict:
        self._ensure_live_runtime_owner(current_user)
        return await self.recognize_fast(
            runtime_id=runtime_id,
            face_files=face_files,
            face_positions_json=face_positions_json,
        )

    def get_stream_packet(self, runtime_id: str) -> Optional[tuple[int, bytes]]:
        with self.runtime.lock:
            if not self.runtime.active or runtime_id != self.runtime.runtime_id:
                return None
            if self.runtime.worker is None:
                return None
            return self.runtime.worker.get_stream_packet()

    def is_runtime_active(self, runtime_id: str) -> bool:
        with self.runtime.lock:
            return self.runtime.active and self.runtime.runtime_id == runtime_id

    def get_results_payload(self, runtime_id: str) -> Optional[dict]:
        with self.runtime.lock:
            if not self.runtime.active or runtime_id != self.runtime.runtime_id:
                return None
            if self.runtime.worker is None:
                return None
            return self.runtime.worker.get_latest_results_payload()

    def _get_cache(self) -> dict:
        with self.runtime.lock:
            return self.runtime.cache_data

    def _is_attended(self, sid: int) -> bool:
        with self.runtime.lock:
            return sid in self.runtime.attended_student_ids

    def _mark_attended(self, sid: int) -> None:
        with self.runtime.lock:
            self.runtime.attended_student_ids.add(sid)

    async def upload_student_faces(self, student_id: int, files) -> dict:
        if self.repo is None:
            raise ValidationException("Repository chưa được khởi tạo", field="repo")
        student = await self.repo.get_active_student_by_id(student_id)
        if student is None:
            raise ValidationException("Sinh viên không tồn tại hoặc đã bị khóa", field="student_id")

        backend_dir = _backend_dir
        image_root = backend_dir / settings.ai_demo_image_dir
        student_dir = image_root / str(student.student_code)
        student_dir.mkdir(parents=True, exist_ok=True)

        allowed_ext = {".jpg", ".jpeg", ".png", ".webp"}
        uploaded_faces = []
        errors = []

        for file in files:
            filename = (file.filename or "").strip()
            if not filename:
                continue

            ext = Path(filename).suffix.lower()
            if ext not in allowed_ext:
                errors.append(f"{filename}: định dạng không hỗ trợ")
                continue

            safe_name = f"{uuid.uuid4().hex}{ext}"
            full_path = student_dir / safe_name

            content = await file.read()
            if not content:
                errors.append(f"{filename}: file rỗng")
                continue

            full_path.write_bytes(content)

            emb = await asyncio.to_thread(extract_embedding_from_path, str(full_path))
            if emb is None:
                full_path.unlink(missing_ok=True)
                errors.append(f"{filename}: không trích xuất được embedding")
                log_ai_demo_event(
                    "upload_face_fail",
                    student_id=int(student_id),
                    filename=filename,
                    reason="extract_embedding_failed",
                )
                continue

            rel_path = full_path.relative_to(backend_dir).as_posix()
            face = await self.repo.add_student_face(
                student_id=student.id,
                image_url=rel_path,
                embedding=emb.tolist(),
            )
            uploaded_faces.append({"id": int(face.id), "image_url": rel_path})
            log_ai_demo_event(
                "upload_face_success",
                student_id=int(student_id),
                face_id=int(face.id),
                image_url=rel_path,
            )

        if uploaded_faces:
            await self.rebuild_cache()

        return {
            "uploaded": len(uploaded_faces),
            "failed": len(errors),
            "faces": uploaded_faces,
            "errors": errors,
        }
