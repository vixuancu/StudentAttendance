from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class AttendanceRecordResponse(BaseModel):
    id: Optional[int] = None
    class_session_id: int
    status: Optional[int] = None
    note: Optional[str] = None
    session_date: datetime
    attendance_created_at: Optional[datetime] = None

class StudentAttendanceMatrixResponse(BaseModel):
    student_id: int
    student_code: str
    full_name: str
    records: List[AttendanceRecordResponse]

class AttendanceMatrixResponse(BaseModel):
    course_section_id: int
    students: List[StudentAttendanceMatrixResponse]
    total_sessions: int
