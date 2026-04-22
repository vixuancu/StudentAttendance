from abc import ABC, abstractmethod
from typing import List, Optional

from src.db.models.attendance import Attendance
from src.db.models.class_session import ClassSession

class IAttendanceRepository(ABC):
    @abstractmethod
    async def get_attendances_by_course_section_and_date_range(
        self,
        course_section_id: int,
        from_date: Optional[object],
        to_date: Optional[object]
    ) -> List[Attendance]:
        pass

    @abstractmethod
    async def get_class_sessions_by_course_section_and_date_range(
        self,
        course_section_id: int,
        from_date: Optional[object],
        to_date: Optional[object]
    ) -> List[ClassSession]:
        pass

    @abstractmethod
    async def get_class_session_by_id(
        self,
        class_session_id: int
    ) -> Optional[ClassSession]:
        pass

    @abstractmethod
    async def get_attendance_by_student_and_session(
        self,
        student_id: int,
        class_session_id: int
    ) -> Optional[Attendance]:
        pass

    @abstractmethod
    async def create_attendance(
        self,
        student_id: int,
        class_session_id: int,
        status: int,
        note: Optional[str]
    ) -> Attendance:
        pass

    @abstractmethod
    async def update_attendance(
        self,
        attendance: Attendance,
        status: Optional[int],
        note: Optional[str]
    ) -> Attendance:
        pass

    @abstractmethod
    async def soft_delete_attendance(
        self,
        attendance: Attendance
    ) -> None:
        pass
