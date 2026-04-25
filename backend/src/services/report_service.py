from typing import List, Optional
from datetime import date

from src.db.models.camera import Camera
from src.db.models.classroom import Classroom
from src.db.models.student import Student
from src.repository.interfaces.i_report_repo import IReportRepository
from src.repository.interfaces.i_student_repo import IStudentRepository
from src.repository.interfaces.i_user_repo import IUserRepository
from src.repository.interfaces.i_camera_repo import ICameraRepository
from src.repository.interfaces.i_classroom_repo import IClassroomRepository
from src.repository.interfaces.i_course_section_repo import ICourseSectionRepository
from src.services.interfaces.i_report_service import IReportService
from src.db.models.enums import AttendanceStatus
from src.dto.response.report_response import (
    ReportStatsResponse,
    ReportOverviewResponse,
    WeeklyTrendItem,
    ClassSummaryItem,
    ReportDetailItem,
    PaginatedReportDetailResponse,
)


class ReportService(IReportService):
    def __init__(
        self,
        report_repo: IReportRepository,
        student_repo: IStudentRepository,
        user_repo: IUserRepository,
        camera_repo: ICameraRepository,
        classroom_repo: IClassroomRepository,
        course_section_repo: ICourseSectionRepository,
    ):
        self.report_repo = report_repo
        self.student_repo = student_repo
        self.user_repo = user_repo
        self.camera_repo = camera_repo
        self.classroom_repo = classroom_repo
        self.course_section_repo = course_section_repo

    async def get_report_stats(
        self,
        course_section_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> ReportStatsResponse:
        data = await self.report_repo.get_report_stats(
            course_section_id, from_date, to_date
        )
        return ReportStatsResponse(**data)

    async def get_overview(self) -> ReportOverviewResponse:
        attendance_stats = await self.report_repo.get_report_stats()

        student_total = await self.student_repo.count(
            filters=[Student.is_cancel.is_(False)]
        )
        lecturer_total = await self.user_repo.count_users(
            role_name="giang_vien", is_cancel=False
        )
        course_section_total = await self.course_section_repo.count_sections(
            None, False
        )
        camera_total = await self.camera_repo.count(
            filters=[Camera.is_cancel.is_(False)]
        )
        camera_online = await self.camera_repo.count(
            filters=[Camera.is_cancel.is_(False), Camera.camera_status == 1]
        )
        room_total = await self.classroom_repo.count(
            filters=[Classroom.is_cancel.is_(False)]
        )

        return ReportOverviewResponse(
            student_total=student_total,
            lecturer_total=lecturer_total,
            course_section_total=course_section_total,
            camera_total=camera_total,
            camera_online=camera_online,
            room_total=room_total,
            attendance_total=attendance_stats["total_records"],
            attendance_present=attendance_stats["co_mat"],
            attendance_late=attendance_stats["tre"],
            attendance_absent=attendance_stats["vang"],
        )

    async def get_weekly_trend(
        self,
        course_section_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> List[WeeklyTrendItem]:
        data = await self.report_repo.get_weekly_trend(
            course_section_id, from_date, to_date
        )
        return [WeeklyTrendItem(**item) for item in data]

    async def get_class_summary(
        self, from_date: Optional[date] = None, to_date: Optional[date] = None
    ) -> List[ClassSummaryItem]:
        data = await self.report_repo.get_class_summary(from_date, to_date)
        return [ClassSummaryItem(**item) for item in data]

    async def get_report_details(
        self,
        course_section_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        page: int = 1,
        per_page: int = 10,
    ) -> PaginatedReportDetailResponse:
        records, total = await self.report_repo.get_report_details(
            course_section_id, from_date, to_date, page, per_page
        )

        detail_items = []
        for record in records:
            student = record.student
            session = record.class_session
            section = session.course_section
            course = section.course

            status_label = "Chưa rõ"
            if record.status == AttendanceStatus.PRESENT:
                status_label = "Có mặt"
            elif record.status == AttendanceStatus.LATE:
                status_label = "Đi trễ"
            elif record.status == AttendanceStatus.ABSENT:
                status_label = "Vắng"
            elif record.status == AttendanceStatus.EXCUSED:
                status_label = "Có phép"

            session_date_str = (
                session.session_date.strftime("%Y-%m-%d")
                if session.session_date
                else ""
            )
            attendance_time = (
                record.created_at.strftime("%H:%M:%S") if record.created_at else None
            )

            detail_items.append(
                ReportDetailItem(
                    id=record.id,
                    student_code=student.student_code if student else "N/A",
                    student_name=student.full_name if student else "N/A",
                    course_name=course.course_name if course else "N/A",
                    course_section_name=section.name if section else "N/A",
                    session_date=session_date_str,
                    attendance_time=attendance_time,
                    status=record.status,
                    status_label=status_label,
                )
            )

        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

        return PaginatedReportDetailResponse(
            data=detail_items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )
