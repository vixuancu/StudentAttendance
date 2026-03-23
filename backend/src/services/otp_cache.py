import threading
import time
from dataclasses import dataclass


@dataclass
class OTPEntry:
    otp: str
    expires_at: float


class OTPMemoryCache:

    def __init__(self) -> None:
        self._store: dict[str, OTPEntry] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    def set(self, email: str, otp: str, ttl_seconds: int) -> None:
        normalized = self._normalize_email(email)
        entry = OTPEntry(
            otp=otp,
            expires_at=time.time() + ttl_seconds,
        )
        with self._lock:
            self._store[normalized] = entry

    def verify(self, email: str, otp: str) -> bool:
        normalized = self._normalize_email(email)
        now = time.time()
        with self._lock:
            entry = self._store.get(normalized)
            if entry is None:
                return False
            if entry.expires_at < now:
                self._store.pop(normalized, None)
                return False
            if entry.otp != otp:
                return False
            self._store.pop(normalized, None)
            return True


otp_memory_cache = OTPMemoryCache()
