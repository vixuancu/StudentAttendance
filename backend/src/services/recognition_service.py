import os
import threading
import time
import traceback
from dataclasses import dataclass
from typing import Callable, Optional

import cv2
import numpy as np

from src.config.settings import settings
from src.utils.ai_demo_logger import log_ai_demo_event

_face_app = None
_rec_model = None
_model_lock = threading.Lock()


def get_face_app():
    global _face_app
    if _face_app is None:
        with _model_lock:
            if _face_app is None:
                import insightface

                _face_app = insightface.app.FaceAnalysis(
                    name=settings.ai_demo_insightface_model,
                    providers=["CPUExecutionProvider"],
                )
                _face_app.prepare(ctx_id=0, det_size=(640, 640))
    return _face_app


def _get_rec_model():
    global _rec_model
    if _rec_model is None:
        app = get_face_app()
        _rec_model = app.models.get("recognition")
    return _rec_model


def _normalize(vec: np.ndarray) -> np.ndarray:
    denom = np.linalg.norm(vec) + 1e-10
    return vec / denom


def compute_face_quality(face_size: int) -> float:
    if face_size >= settings.ai_demo_quality_face_size_good:
        return 1.0
    if face_size <= settings.ai_demo_quality_face_size_min:
        return 0.0
    return (face_size - settings.ai_demo_quality_face_size_min) / (
        settings.ai_demo_quality_face_size_good - settings.ai_demo_quality_face_size_min
    )


def adaptive_threshold(face_quality: float) -> float:
    penalty = (1.0 - face_quality) * settings.ai_demo_quality_threshold_penalty
    return settings.ai_demo_cosine_threshold + penalty


def build_cache_from_rows(rows: list[dict]) -> dict:
    embeddings = []
    student_ids = []
    metadata = {}

    dim = 512
    for row in rows:
        emb = row.get("embedding")
        if emb is None:
            continue
        arr = np.asarray(emb, dtype=np.float32)
        if arr.ndim != 1:
            continue
        if arr.shape[0] != dim:
            continue
        embeddings.append(arr)
        sid = int(row["student_id"])
        student_ids.append(sid)
        if sid not in metadata:
            metadata[sid] = {
                "student_code": row["student_code"],
                "full_name": row["full_name"],
            }

    if embeddings:
        matrix = np.vstack(embeddings).astype(np.float32)
    else:
        matrix = np.empty((0, dim), dtype=np.float32)

    return {
        "embeddings": matrix,
        "student_ids": student_ids,
        "metadata": metadata,
        "n_students": len(metadata),
        "n_embeddings": int(matrix.shape[0]),
        "loaded_at": time.time(),
    }


def match_from_cache(
    face_embedding: np.ndarray, cache_data: dict, face_quality: float
) -> tuple[Optional[dict], float, dict]:
    emb_matrix: np.ndarray = cache_data["embeddings"]
    student_ids: list[int] = cache_data["student_ids"]
    metadata: dict = cache_data["metadata"]

    if emb_matrix.size == 0:
        return None, 0.0, {"reason": "empty_cache"}

    query = _normalize(np.asarray(face_embedding, dtype=np.float32))
    norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    emb_normed = emb_matrix / norms
    similarities = emb_normed @ query

    per_student = {}
    for i, sim in enumerate(similarities):
        sid = student_ids[i]
        if sid not in per_student:
            meta = metadata.get(sid, {"student_code": "?", "full_name": "?"})
            per_student[sid] = {
                "student_id": sid,
                "student_code": meta["student_code"],
                "full_name": meta["full_name"],
                "scores": [],
            }
        per_student[sid]["scores"].append(float(sim))

    for info in per_student.values():
        scores = sorted(info["scores"], reverse=True)
        top_n = scores[: min(settings.ai_demo_student_agg_top_n, len(scores))]
        info["agg_score"] = sum(top_n) / len(top_n)

    ranked = sorted(per_student.values(), key=lambda x: x["agg_score"], reverse=True)
    best = ranked[0]
    second = ranked[1] if len(ranked) > 1 else None

    threshold = adaptive_threshold(face_quality)
    margin = best["agg_score"] - (second["agg_score"] if second else 0.0)
    debug = {
        "threshold": round(threshold, 4),
        "margin": round(margin, 4),
        "best": round(best["agg_score"], 4),
    }

    if best["agg_score"] < threshold:
        debug["reason"] = "below_threshold"
        return None, 0.0, debug

    if second and margin < settings.ai_demo_match_margin_min:
        debug["reason"] = "margin_too_small"
        return None, 0.0, debug

    debug["reason"] = "matched"
    return (
        {
            "student_id": best["student_id"],
            "student_code": best["student_code"],
            "full_name": best["full_name"],
        },
        float(best["agg_score"]),
        debug,
    )


def extract_embedding_from_path(image_path: str) -> Optional[np.ndarray]:
    img = cv2.imread(image_path)
    if img is None:
        return None

    app = get_face_app()
    faces = app.get(img)
    if not faces:
        return None

    best = max(faces, key=lambda f: float(getattr(f, "det_score", 0.0)))
    det_score = float(getattr(best, "det_score", 0.0))
    if det_score < settings.ai_demo_face_confidence_min:
        return None

    emb = np.asarray(best.embedding, dtype=np.float32)
    if emb.shape[0] != 512:
        return None
    return _normalize(emb)


def extract_embeddings_from_frame(frame: np.ndarray) -> list[dict]:
    app = get_face_app()
    faces = app.get(frame)
    results = []
    for f in faces:
        x1, y1, x2, y2 = (int(v) for v in f.bbox[:4])
        w = max(1, x2 - x1)
        h = max(1, y2 - y1)
        size = max(w, h)
        quality = compute_face_quality(size)
        det_score = float(getattr(f, "det_score", 0.0))
        results.append(
            {
                "embedding": np.asarray(f.embedding, dtype=np.float32),
                "face_box": {"x": x1, "y": y1, "w": w, "h": h},
                "quality": quality,
                "det_score": det_score,
            }
        )
    return results


def extract_embeddings_from_crops(
    crops: list[np.ndarray],
) -> list[tuple[Optional[np.ndarray], float]]:
    app = get_face_app()
    rec_model = _get_rec_model()
    outputs = []

    for crop in crops:
        if crop is None or crop.size == 0:
            outputs.append((None, 0.0))
            continue

        h, w = crop.shape[:2]
        face_size = max(h, w)
        quality = compute_face_quality(face_size)

        try:
            pad_h = int(h * 0.5)
            pad_w = int(w * 0.5)
            padded = cv2.copyMakeBorder(
                crop,
                pad_h,
                pad_h,
                pad_w,
                pad_w,
                cv2.BORDER_CONSTANT,
                value=(0, 0, 0),
            )

            pf = app.get(padded)
            if pf:
                best = max(pf, key=lambda f: float(getattr(f, "det_score", 0.0)))
                outputs.append((np.asarray(best.embedding, dtype=np.float32), quality))
                continue

            if rec_model is None:
                outputs.append((None, 0.0))
                continue

            aligned = cv2.resize(crop, (112, 112), interpolation=cv2.INTER_CUBIC)
            blob = cv2.dnn.blobFromImage(
                aligned,
                1.0 / 127.5,
                (112, 112),
                (127.5, 127.5, 127.5),
                swapRB=True,
            )
            emb = rec_model.session.run(
                rec_model.output_names,
                {rec_model.input_names[0]: blob},
            )[0][0]
            outputs.append((np.asarray(emb, dtype=np.float32), quality * 0.7))
        except Exception:
            outputs.append((None, 0.0))

    return outputs


@dataclass
class RuntimeState:
    active: bool = False
    mode: str = "webcam"
    runtime_id: str = ""
    started_at: float = 0.0
    rtsp_url: str = ""


class AIDemoRTSPWorker:
    def __init__(
        self,
        rtsp_url: str,
        get_cache: Callable[[], dict],
        is_attended: Callable[[int], bool],
        mark_attended: Callable[[int], None],
        runtime_id: str,
    ):
        self.rtsp_url = rtsp_url.replace(" ", "")
        self._get_cache = get_cache
        self._is_attended = is_attended
        self._mark_attended = mark_attended
        self.runtime_id = runtime_id

        self.running = False
        self.connected = False
        self.processed_count = 0
        self.attended_count = 0

        self._latest_frame = None
        self._latest_jpeg_bytes = None
        self._latest_jpeg_seq = 0
        self._latest_results = []
        self._latest_result_frame_size = (0, 0)
        self._new_frame_event = threading.Event()
        self._pending_confirm = {}
        self._lock = threading.Lock()
        self._cap = None

        self._reader_thread = None
        self._encoder_thread = None
        self._processor_thread = None
        self._capture_preset = self._normalize_capture_preset(
            settings.ai_demo_rtsp_capture_preset
        )

    @staticmethod
    def _normalize_capture_preset(raw: str | None) -> str:
        preset = (raw or "stable").strip().lower()
        if preset not in {"stable", "low_latency"}:
            return "stable"
        return preset

    def _apply_capture_options(self, preset: str) -> None:
        if preset == "low_latency":
            options = "rtsp_transport;tcp|fflags;nobuffer|flags;low_delay"
        else:
            options = "rtsp_transport;tcp|max_delay;500000|reorder_queue_size;32|buffer_size;1048576"
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = options

    @staticmethod
    def _is_corrupted_frame(frame: np.ndarray | None) -> bool:
        if frame is None or frame.size == 0:
            return True
        if frame.ndim != 3 or frame.shape[2] != 3:
            return True
        std_val = float(np.std(frame))
        return std_val < float(settings.ai_demo_rtsp_corrupt_min_std)

    def _next_preset_after_fail(self, current_preset: str) -> str:
        if not settings.ai_demo_rtsp_enable_preset_fallback:
            return current_preset
        if current_preset == "low_latency":
            return "stable"
        return "stable"

    def start(self):
        self.running = True
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._encoder_thread = threading.Thread(target=self._encoder_loop, daemon=True)
        self._processor_thread = threading.Thread(
            target=self._processor_loop, daemon=True
        )
        self._reader_thread.start()
        self._encoder_thread.start()
        self._processor_thread.start()

    def stop(self):
        self.running = False
        if self._cap is not None:
            self._cap.release()
        for thread in (
            self._reader_thread,
            self._encoder_thread,
            self._processor_thread,
        ):
            if thread:
                thread.join(timeout=2)

    def get_stream_packet(self) -> Optional[tuple[int, bytes]]:
        with self._lock:
            if self._latest_jpeg_bytes is None:
                return None
            return self._latest_jpeg_seq, self._latest_jpeg_bytes

    def get_latest_results_payload(self) -> dict:
        with self._lock:
            fw, fh = self._latest_result_frame_size
            return {
                "faces": self._latest_results.copy(),
                "frame_width": fw,
                "frame_height": fh,
                "connected": self.connected,
                "total_attended": self.attended_count,
                "processed_count": self.processed_count,
            }

    def _reader_loop(self):
        while self.running:
            self._apply_capture_options(self._capture_preset)
            self._cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            consecutive_read_fail = 0
            consecutive_corrupt = 0

            if not self._cap.isOpened():
                self.connected = False
                log_ai_demo_event(
                    "rtsp_connect_fail",
                    runtime_id=self.runtime_id,
                    rtsp_url=self.rtsp_url,
                    capture_preset=self._capture_preset,
                )
                time.sleep(settings.ai_demo_rtsp_reconnect_delay)
                continue

            self.connected = True
            log_ai_demo_event(
                "rtsp_connected",
                runtime_id=self.runtime_id,
                rtsp_url=self.rtsp_url,
                capture_preset=self._capture_preset,
            )

            while self.running and self._cap.isOpened():
                ok, frame = self._cap.read()
                if not ok:
                    consecutive_read_fail += 1
                    if settings.ai_demo_debug_log_verbose:
                        log_ai_demo_event(
                            "rtsp_frame_read_fail",
                            runtime_id=self.runtime_id,
                            consecutive=consecutive_read_fail,
                        )
                    if consecutive_read_fail < max(
                        1, settings.ai_demo_rtsp_read_fail_tolerance
                    ):
                        time.sleep(0.01)
                        continue
                    self.connected = False
                    break
                consecutive_read_fail = 0

                if self._is_corrupted_frame(frame):
                    consecutive_corrupt += 1
                    if settings.ai_demo_debug_log_verbose:
                        log_ai_demo_event(
                            "rtsp_frame_corrupt",
                            runtime_id=self.runtime_id,
                            consecutive=consecutive_corrupt,
                            capture_preset=self._capture_preset,
                        )
                    if consecutive_corrupt < max(
                        1, settings.ai_demo_rtsp_corrupt_frame_tolerance
                    ):
                        continue
                    self.connected = False
                    break

                consecutive_corrupt = 0
                with self._lock:
                    self._latest_frame = frame
                self._new_frame_event.set()

            if self._cap is not None:
                self._cap.release()
            self.connected = False
            log_ai_demo_event(
                "rtsp_disconnected",
                runtime_id=self.runtime_id,
                capture_preset=self._capture_preset,
            )

            if self.running and settings.ai_demo_rtsp_enable_preset_fallback:
                next_preset = self._next_preset_after_fail(self._capture_preset)
                if next_preset != self._capture_preset:
                    log_ai_demo_event(
                        "rtsp_capture_preset_switch",
                        runtime_id=self.runtime_id,
                        from_preset=self._capture_preset,
                        to_preset=next_preset,
                    )
                    self._capture_preset = next_preset

    def _encoder_loop(self):
        interval = 1.0 / max(1, settings.ai_demo_rtsp_stream_fps)
        next_at = 0.0

        while self.running:
            self._new_frame_event.wait(timeout=interval)
            self._new_frame_event.clear()

            now = time.perf_counter()
            if now < next_at:
                continue

            with self._lock:
                frame = (
                    self._latest_frame.copy()
                    if self._latest_frame is not None
                    else None
                )

            if frame is None:
                continue

            h, w = frame.shape[:2]
            if (
                w > settings.ai_demo_rtsp_frame_width
                or h > settings.ai_demo_rtsp_frame_height
            ):
                frame = cv2.resize(
                    frame,
                    (
                        settings.ai_demo_rtsp_frame_width,
                        settings.ai_demo_rtsp_frame_height,
                    ),
                    interpolation=cv2.INTER_AREA,
                )

            ok, buf = cv2.imencode(
                ".jpg",
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), settings.ai_demo_rtsp_jpeg_quality],
            )
            if ok:
                with self._lock:
                    self._latest_jpeg_bytes = buf.tobytes()
                    self._latest_jpeg_seq += 1
                next_at = now + interval

    def _processor_loop(self):
        get_face_app()
        while self.running:
            time.sleep(settings.ai_demo_rtsp_process_interval)
            with self._lock:
                frame = (
                    self._latest_frame.copy()
                    if self._latest_frame is not None
                    else None
                )
            if frame is None:
                continue
            try:
                self._process_frame(frame)
            except Exception:
                traceback.print_exc()

    def _process_frame(self, frame: np.ndarray):
        cache = self._get_cache()
        if not cache or cache["embeddings"].size == 0:
            return

        faces = extract_embeddings_from_frame(frame)
        frame_h, frame_w = frame.shape[:2]
        now_ts = time.time()
        results = []

        stale = [
            k
            for k, v in self._pending_confirm.items()
            if now_ts - v.get("updated_at", 0)
            > settings.ai_demo_rtsp_confirm_streak_ttl
        ]
        for k in stale:
            self._pending_confirm.pop(k, None)

        for item in faces:
            emb = item["embedding"]
            quality = float(item["quality"])
            det_score = float(item["det_score"])
            box = item["face_box"]
            size = max(int(box["w"]), int(box["h"]))

            if (
                det_score < settings.ai_demo_rtsp_min_det_score
                or size < settings.ai_demo_rtsp_min_face_size
            ):
                results.append(
                    {"recognized": False, "status": "focusing", "face_box": box}
                )
                continue

            if quality < settings.ai_demo_rtsp_min_face_quality:
                results.append(
                    {"recognized": False, "status": "focusing", "face_box": box}
                )
                continue

            match, score, dbg = match_from_cache(emb, cache, quality)
            margin = float(dbg.get("margin", 0.0)) if isinstance(dbg, dict) else 0.0

            if (
                match is None
                or score < settings.ai_demo_rtsp_confirm_min_confidence
                or margin < settings.ai_demo_rtsp_confirm_min_margin
            ):
                if settings.ai_demo_debug_log_verbose:
                    log_ai_demo_event(
                        "rtsp_match_reject",
                        runtime_id=self.runtime_id,
                        reason=(
                            dbg.get("reason") if isinstance(dbg, dict) else "unmatched"
                        ),
                        score=round(float(score), 4),
                        margin=round(float(margin), 4),
                        quality=round(float(quality), 4),
                        best=(dbg.get("best") if isinstance(dbg, dict) else None),
                        threshold=(
                            dbg.get("threshold") if isinstance(dbg, dict) else None
                        ),
                    )
                results.append(
                    {"recognized": False, "status": "focusing", "face_box": box}
                )
                continue

            one_shot = (
                score >= settings.ai_demo_rtsp_one_shot_confidence
                and quality >= settings.ai_demo_rtsp_min_face_quality_one_shot
                and margin >= settings.ai_demo_rtsp_one_shot_min_margin
            )
            required = 1 if one_shot else 2

            key = str(match["student_id"])
            state = self._pending_confirm.get(key)
            if (
                state
                and now_ts - state.get("updated_at", 0)
                <= settings.ai_demo_rtsp_confirm_streak_ttl
            ):
                hits = int(state.get("hits", 0)) + 1
            else:
                hits = 1

            self._pending_confirm[key] = {
                "hits": hits,
                "updated_at": now_ts,
                "required_hits": required,
            }

            if hits < required:
                results.append(
                    {
                        "recognized": False,
                        "status": "confirming",
                        "confirm_hits": hits,
                        "confirm_required": required,
                        "face_box": box,
                    }
                )
                continue

            self._pending_confirm.pop(key, None)
            sid = int(match["student_id"])
            already = self._is_attended(sid)
            if not already:
                self._mark_attended(sid)
                self.attended_count += 1

            results.append(
                {
                    "recognized": True,
                    "student_code": match["student_code"],
                    "full_name": match["full_name"],
                    "confidence": round(float(score) * 100, 1),
                    "already_marked": already,
                    "face_box": box,
                }
            )
            if settings.ai_demo_debug_log_verbose:
                log_ai_demo_event(
                    "rtsp_match_accept",
                    runtime_id=self.runtime_id,
                    student_id=sid,
                    student_code=match["student_code"],
                    score=round(float(score), 4),
                    quality=round(float(quality), 4),
                    margin=round(float(margin), 4),
                    already_marked=already,
                )

        self.processed_count += 1
        with self._lock:
            self._latest_results = results
            self._latest_result_frame_size = (frame_w, frame_h)
