import math
from datetime import datetime

from src.db.models.course_section import CourseSection
from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.course_section_request import (
    CourseSectionEnrollmentCreateRequest,
    CourseSectionCreateRequest,
    CourseSectionUpdateRequest,
)
from src.dto.response.course_section_response import (
    CourseSectionFormOptionsResponse,
    CourseSectionOptionResponse,
    CourseSectionResponse,
    CourseSectionScheduleResponse,
)
from src.dto.response.student_response import StudentResponse
from src.dto.response.student_response import StudentImportResultResponse
from src.services.interfaces.i_course_section_service import ICourseSectionService


class CourseSectionController:

    def __init__(self, service: ICourseSectionService):
        self.service = service

    @staticmethod
    def _resolve_semester(start_date: datetime, end_date: datetime) -> str:
        semester = 1 if start_date.month <= 6 else 2
        return f"{start_date.year}-{end_date.year}.{semester}"

    @staticmethod
    def _resolve_day_label(day_of_week: int) -> str:
        labels = {
            2: "Thứ 2",
            3: "Thứ 3",
            4: "Thứ 4",
            5: "Thứ 5",
            6: "Thứ 6",
            7: "Thứ 7",
            8: "Chủ nhật",
        }
        return labels.get(day_of_week, f"Thứ {day_of_week}")

    @classmethod
    def _to_response(
        cls, section: CourseSection, si_so: int = 0
    ) -> CourseSectionResponse:
        return CourseSectionResponse(
            id=section.id,
            name=section.name,
            course_id=section.course_id,
            course_name=section.course.course_name if section.course else "",
            user_id=section.user_id,
            user_full_name=section.user.full_name if section.user else None,
            room_id=section.room_id,
            room_name=section.room.class_name if section.room else "",
            day_of_week=section.day_of_week,
            start_date=section.start_date,
            end_date=section.end_date,
            start_period=section.start_period,
            number_of_periods=section.number_of_periods,
            start_time=section.start_time,
            end_time=section.end_time,
            hoc_ky=cls._resolve_semester(section.start_date, section.end_date),
            si_so=si_so,
            is_cancel=section.is_cancel,
            created_at=section.created_at,
            updated_at=section.updated_at,
            schedules=[
                CourseSectionScheduleResponse(
                    id=schedule.id,
                    course_section_id=schedule.course_section_id,
                    user_id=schedule.user_id,
                    user_full_name=schedule.user.full_name if schedule.user else None,
                    day_of_week=schedule.day_of_week,
                    day_of_week_label=cls._resolve_day_label(schedule.day_of_week),
                    start_period=schedule.start_period,
                    number_of_periods=schedule.number_of_periods,
                    end_period=schedule.start_period + schedule.number_of_periods - 1,
                    start_time=schedule.start_time,
                    end_time=schedule.end_time,
                    room_id=schedule.room_id,
                    room_name=schedule.room.class_name if schedule.room else None,
                    display_text=(
                        f"{cls._resolve_day_label(schedule.day_of_week)} - "
                        f"Tiết {schedule.start_period}-{schedule.start_period + schedule.number_of_periods - 1}"
                    ),
                    is_cancel=schedule.is_cancel,
                    created_at=schedule.created_at,
                    updated_at=schedule.updated_at,
                )
                for schedule in sorted(
                    [s for s in (section.schedules or []) if not s.is_cancel],
                    key=lambda s: (s.day_of_week, s.start_period, s.id),
                )
            ],
        )

    async def list_sections(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        is_cancel: bool | None = None,
    ) -> ListResponse[CourseSectionResponse]:
        items, total = await self.service.list_sections(pagination, search, is_cancel)

        return ListResponse(
            data=[self._to_response(section, si_so) for section, si_so in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=math.ceil(total / pagination.page_size) if total else 0,
        )

    async def get_by_id(self, section_id: int) -> DataResponse[CourseSectionResponse]:
        item = await self.service.get_by_id(section_id)
        return DataResponse(
            data=self._to_response(item),
            message="Lấy lớp tín chỉ thành công",
        )

    async def create(
        self,
        request: CourseSectionCreateRequest,
    ) -> DataResponse[CourseSectionResponse]:
        item = await self.service.create(request)
        return DataResponse(
            data=self._to_response(item),
            message="Tạo lớp tín chỉ thành công",
        )

    async def update(
        self,
        section_id: int,
        request: CourseSectionUpdateRequest,
    ) -> DataResponse[CourseSectionResponse]:
        item = await self.service.update(section_id, request)
        return DataResponse(
            data=self._to_response(item),
            message="Cập nhật lớp tín chỉ thành công",
        )

    async def delete(self, section_id: int) -> DataResponse[None]:
        await self.service.delete(section_id)
        return DataResponse(message="Xóa lớp tín chỉ thành công")

    async def get_form_options(self) -> DataResponse[CourseSectionFormOptionsResponse]:
        courses, lecturers, rooms = await self.service.get_form_options()
        return DataResponse(
            data=CourseSectionFormOptionsResponse(
                courses=[
                    CourseSectionOptionResponse(
                        id=course.id,
                        name=course.course_name or "",
                    )
                    for course in courses
                ],
                lecturers=[
                    CourseSectionOptionResponse(
                        id=user.id,
                        name=user.full_name or user.username,
                    )
                    for user in lecturers
                ],
                rooms=[
                    CourseSectionOptionResponse(
                        id=room.id,
                        name=room.class_name,
                    )
                    for room in rooms
                ],
            )
        )

    @staticmethod
    def _to_student_response(student) -> StudentResponse:
        administrative_class = student.__dict__.get("administrative_class")
        return StudentResponse(
            id=student.id,
            student_code=student.student_code,
            full_name=student.full_name,
            birth_of_date=student.birth_of_date,
            gender=student.gender,
            administrative_class_id=student.administrative_class_id,
            administrative_class_name=(
                administrative_class.name if administrative_class else None
            ),
            face_count=getattr(student, "face_count", 0),
            is_cancel=student.is_cancel,
            created_at=student.created_at,
            updated_at=student.updated_at,
        )

    async def list_section_students(
        self,
        section_id: int,
        pagination: PaginationParams,
        search: str | None = None,
    ) -> ListResponse[StudentResponse]:
        students, total = await self.service.list_enrolled_students(
            section_id, pagination, search
        )
        return ListResponse(
            data=[self._to_student_response(student) for student in students],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=math.ceil(total / pagination.page_size) if total else 0,
        )

    async def add_student_to_section(
        self,
        section_id: int,
        request: CourseSectionEnrollmentCreateRequest,
    ) -> DataResponse[StudentResponse]:
        student = await self.service.add_student_to_section(section_id, request)
        return DataResponse(
            data=self._to_student_response(student),
            message="Thêm sinh viên vào lớp tín chỉ thành công",
        )

    async def remove_student_from_section(
        self,
        section_id: int,
        student_id: int,
    ) -> DataResponse[None]:
        await self.service.remove_student_from_section(section_id, student_id)
        return DataResponse(message="Xóa sinh viên khỏi lớp tín chỉ thành công")

    async def download_student_import_template(self, section_id: int) -> bytes:
        return await self.service.build_student_import_template(section_id)

    async def import_students_to_section(
        self,
        section_id: int,
        file_content: bytes,
        filename: str | None = None,
    ) -> DataResponse[StudentImportResultResponse]:
        result = await self.service.import_students_from_excel(
            section_id=section_id,
            file_content=file_content,
            filename=filename,
        )
        return DataResponse(
            data=result,
            message="Import sinh viên vào lớp tín chỉ hoàn tất",
        )
