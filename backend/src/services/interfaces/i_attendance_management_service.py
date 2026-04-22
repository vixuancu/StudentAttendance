from abc import ABC, abstractmethod
from typing import Optional
from datetime import date

from src.db.models.user import User
from src.dto.request.attendance_management_request import AttendanceUpdateCellRequest
from src.dto.response.attendance_management_response import AttendanceMatrixResponse

class IAttendanceManagementService(ABC):
    @abstractmethod
    async def get_attendance_matrix(
        self,
        course_section_id: int,
        from_date: Optional[date],
        to_date: Optional[date],
        current_user: User
    ) -> AttendanceMatrixResponse:
        pass

    @abstractmethod
    async def update_attendance_cell(
        self,
        request: AttendanceUpdateCellRequest,
        current_user: User
    ) -> dict:
        pass