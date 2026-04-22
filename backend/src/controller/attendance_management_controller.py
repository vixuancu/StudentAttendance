from typing import Optional
from datetime import date

from src.dto.common import DataResponse
from src.db.models.user import User
from src.services.interfaces.i_attendance_management_service import IAttendanceManagementService
from src.dto.request.attendance_management_request import AttendanceUpdateCellRequest
from src.dto.response.attendance_management_response import AttendanceMatrixResponse

class AttendanceManagementController:
    def __init__(self, service: IAttendanceManagementService):
        self.service = service

    async def get_attendance_matrix(
        self,
        course_section_id: int,
        from_date: Optional[date],
        to_date: Optional[date],
        current_user: User
    ) -> DataResponse[AttendanceMatrixResponse]:
        data = await self.service.get_attendance_matrix(
            course_section_id, from_date, to_date, current_user
        )
        return DataResponse(
            data=data,
            message="Lấy dữ liệu điểm danh thành công",
        )

    async def update_attendance_cell(
        self,
        request: AttendanceUpdateCellRequest,
        current_user: User
    ) -> DataResponse[dict]:
        data = await self.service.update_attendance_cell(request, current_user)
        return DataResponse(
            data=data,
            message="Cập nhật điểm danh thành công",
        )