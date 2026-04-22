from typing import Optional
from pydantic import BaseModel, Field


class AttendanceUpdateCellRequest(BaseModel):
    student_id: int = Field(..., description="ID của sinh viên")
    class_session_id: int = Field(..., description="ID của buổi học")
    status: Optional[int] = Field(
        default=None,
        ge=1,
        le=3,
        description="Trạng thái điểm danh (1: Có mặt, 2: Vắng, 3: Đi muộn). Để null để xóa dữ liệu điểm danh của ô"
    )
    note: Optional[str] = Field(default=None, description="Ghi chú điểm danh")
