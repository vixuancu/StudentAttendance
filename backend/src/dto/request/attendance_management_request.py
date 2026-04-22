from typing import Optional
from pydantic import BaseModel, Field


class AttendanceUpdateCellRequest(BaseModel):
    student_id: int = Field(..., description="ID của sinh viên")
    class_session_id: int = Field(..., description="ID của buổi học")
    status: int = Field(..., description="Trạng thái điểm danh (ví dụ: 1: Có mặt, 2: Vắng, 3: Đi muộn)")
    note: Optional[str] = Field(default=None, description="Ghi chú điểm danh")