from pydantic import BaseModel
from typing import List, Optional

class ReportStatsResponse(BaseModel):
    total_records: int
    co_mat: int
    tre: int
    vang: int

class WeeklyTrendItem(BaseModel):
    week_label: str
    week_start: str
    co_mat: float
    tre: float
    vang: float

class ClassSummaryItem(BaseModel):
    course_section_id: int
    course_section_name: str
    course_name: str
    attendance_rate: float

class ReportDetailItem(BaseModel):
    id: Optional[int]
    student_code: str
    student_name: str
    course_name: str
    course_section_name: str
    session_date: str
    attendance_time: Optional[str]
    status: Optional[int]
    status_label: str

class PaginatedReportDetailResponse(BaseModel):
    data: List[ReportDetailItem]
    total: int
    page: int
    per_page: int
    total_pages: int
