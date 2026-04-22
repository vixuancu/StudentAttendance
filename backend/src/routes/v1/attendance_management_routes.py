from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query

from src.controller.attendance_management_controller import AttendanceManagementController
from src.db.models.user import User
from src.dto.common import DataResponse
from src.dto.request.attendance_management_request import AttendanceUpdateCellRequest
from src.dto.response.attendance_management_response import AttendanceMatrixResponse
from src.middleware.auth import require_roles
from src.deps import get_attendance_management_controller

router = APIRouter(prefix="/attendance-management", tags=["Attendance Management"])

@router.get("/matrix", response_model=DataResponse[AttendanceMatrixResponse])
async def get_attendance_matrix(
    course_section_id: int = Query(..., description="ID của lớp tín chỉ"),
    from_date: Optional[date] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
    current_user: User = Depends(require_roles("admin", "giao_vu", "giang_vien")),
    ctrl: AttendanceManagementController = Depends(get_attendance_management_controller)
):
    return await ctrl.get_attendance_matrix(
        course_section_id=course_section_id,
        from_date=from_date,
        to_date=to_date,
        current_user=current_user
    )

@router.patch("/cell", response_model=DataResponse[dict])
async def update_attendance_cell(
    request: AttendanceUpdateCellRequest,
    current_user: User = Depends(require_roles("admin", "giao_vu", "giang_vien")),
    ctrl: AttendanceManagementController = Depends(get_attendance_management_controller)
):
    return await ctrl.update_attendance_cell(request, current_user)