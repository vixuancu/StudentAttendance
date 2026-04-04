from datetime import datetime
from io import BytesIO
import re
import unicodedata
from typing import Optional

from openpyxl import Workbook, load_workbook

from src.constant.error_code import ERROR_CODES
from src.db.models.course_section import CourseSection
from src.db.models.student import Student
from src.dto.common import PaginationParams
from src.dto.request.course_section_request import (
    CourseSectionEnrollmentCreateRequest,
    CourseSectionCreateRequest,
    CourseSectionUpdateRequest,
)
from src.dto.response.student_response import (
    StudentImportErrorResponse,
    StudentImportResultResponse,
)
from src.repository.interfaces.i_course_section_repo import ICourseSectionRepository
from src.services.interfaces.i_course_section_service import ICourseSectionService
from src.utils.exception import AlreadyExists, NotFound, Validation


class CourseSectionService(ICourseSectionService):

    HEADER_ALIASES = {
        "student_code": {
            "masinhvien",
            "mssv",
            "studentcode",
            "code",
        }
    }

    def __init__(self, repo: ICourseSectionRepository):
        self.repo = repo

    @staticmethod
    def _normalize_text(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value.strip().lower())
        normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        normalized = re.sub(r"[^a-z0-9]+", "", normalized)
        return normalized

    @staticmethod
    def _stringify_cell(value) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        return str(value).strip()

    def _build_header_index(self, headers: list[str]) -> dict[str, int]:
        mapped: dict[str, int] = {}
        for idx, raw in enumerate(headers):
            key = self._normalize_text(raw)
            if not key:
                continue
            for column, aliases in self.HEADER_ALIASES.items():
                if key in aliases and column not in mapped:
                    mapped[column] = idx
                    break
        return mapped

    @staticmethod
    def _validate_file_extension(filename: str | None) -> None:
        if not filename:
            return
        lower_name = filename.lower()
        if lower_name.endswith(".xlsx"):
            return
        if lower_name.endswith(".xls"):
            raise Validation(
                message="Định dạng .xls chưa được hỗ trợ, vui lòng lưu file dưới dạng .xlsx"
            )
        raise Validation(message="Chỉ hỗ trợ file Excel định dạng .xlsx")

    @staticmethod
    def _append_import_error(
        errors: list[StudentImportErrorResponse],
        row: int,
        field: str,
        message: str,
        student_code: str | None = None,
    ) -> None:
        errors.append(
            StudentImportErrorResponse(
                row=row,
                field=field,
                student_code=student_code,
                message=message,
            )
        )

    async def list_sections(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> tuple[list[tuple[CourseSection, int]], int]:
        items = await self.repo.list_sections(
            skip=pagination.offset,
            limit=pagination.limit,
            search=search,
            is_cancel=is_cancel,
        )
        total = await self.repo.count_sections(
            search=search,
            is_cancel=is_cancel,
        )
        return items, total

    async def get_by_id(self, section_id: int) -> CourseSection:
        item = await self.repo.get_by_id(section_id)
        if item is None:
            raise NotFound(ERROR_CODES.COURSE_SECTION.COURSE_SECTION_NOT_FOUND)
        return item

    async def _validate_foreign_keys(
        self,
        course_id: Optional[int],
        user_id: Optional[int],
        room_id: Optional[int],
    ):
        if course_id is not None:
            course = await self.repo.get_course_by_id(course_id)
            if course is None:
                raise NotFound(ERROR_CODES.COURSE.COURSE_NOT_FOUND)

        if user_id is not None:
            lecturer = await self.repo.get_lecturer_by_id(user_id)
            if lecturer is None:
                raise NotFound(ERROR_CODES.COURSE_SECTION.LECTURER_NOT_FOUND)

        if room_id is not None:
            room = await self.repo.get_room_by_id(room_id)
            if room is None:
                raise NotFound(ERROR_CODES.CLASSROOM.CLASSROOM_NOT_FOUND)

    @staticmethod
    def _validate_time_fields(
        start_date: datetime,
        end_date: datetime,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
    ):
        if start_date >= end_date:
            raise Validation(
                message="Ngày bắt đầu phải nhỏ hơn ngày kết thúc",
                error_code=ERROR_CODES.COURSE_SECTION.INVALID_DATE_RANGE,
            )

        if start_time is not None and end_time is not None and start_time >= end_time:
            raise Validation(
                message="Giờ bắt đầu phải nhỏ hơn giờ kết thúc",
                error_code=ERROR_CODES.COURSE_SECTION.INVALID_TIME_RANGE,
            )

    async def create(self, request: CourseSectionCreateRequest) -> CourseSection:
        normalized_name = request.name.strip()
        existed = await self.repo.get_by_name_ci(normalized_name)
        if existed is not None:
            raise AlreadyExists(
                ERROR_CODES.COURSE_SECTION.COURSE_SECTION_NAME_IS_EXISTED
            )

        await self._validate_foreign_keys(
            course_id=request.course_id,
            user_id=request.user_id,
            room_id=request.room_id,
        )

        self._validate_time_fields(
            start_date=request.start_date,
            end_date=request.end_date,
            start_time=request.start_time,
            end_time=request.end_time,
        )

        data = request.model_dump()
        data["name"] = normalized_name
        data["is_cancel"] = False

        created = await self.repo.create(data)
        refreshed = await self.repo.get_by_id(created.id)
        return refreshed if refreshed is not None else created

    async def update(
        self,
        section_id: int,
        request: CourseSectionUpdateRequest,
    ) -> CourseSection:
        item = await self.get_by_id(section_id)
        data = request.model_dump(exclude_unset=True)

        if "name" in data and data["name"] is not None:
            normalized_name = data["name"].strip()
            existed = await self.repo.get_by_name_ci(normalized_name)
            if existed is not None and existed.id != item.id:
                raise AlreadyExists(
                    ERROR_CODES.COURSE_SECTION.COURSE_SECTION_NAME_IS_EXISTED
                )
            data["name"] = normalized_name

        await self._validate_foreign_keys(
            course_id=data.get("course_id"),
            user_id=data.get("user_id"),
            room_id=data.get("room_id"),
        )

        start_date = data.get("start_date", item.start_date)
        end_date = data.get("end_date", item.end_date)
        start_time = data.get("start_time", item.start_time)
        end_time = data.get("end_time", item.end_time)
        self._validate_time_fields(start_date, end_date, start_time, end_time)

        updated = await self.repo.update(item, data)
        refreshed = await self.repo.get_by_id(updated.id)
        return refreshed if refreshed is not None else updated

    async def delete(self, section_id: int) -> CourseSection:
        item = await self.get_by_id(section_id)
        return await self.repo.soft_delete(item)

    async def get_form_options(self):
        courses = await self.repo.list_course_options()
        lecturers = await self.repo.list_lecturer_options()
        rooms = await self.repo.list_room_options()
        return courses, lecturers, rooms

    async def list_enrolled_students(
        self,
        section_id: int,
        pagination: PaginationParams,
        search: Optional[str] = None,
    ) -> tuple[list[Student], int]:
        await self.get_by_id(section_id)

        students = await self.repo.list_enrolled_students(
            section_id=section_id,
            skip=pagination.offset,
            limit=pagination.limit,
            search=search,
        )
        total = await self.repo.count_enrolled_students(
            section_id=section_id, search=search
        )
        return students, total

    async def add_student_to_section(
        self,
        section_id: int,
        request: CourseSectionEnrollmentCreateRequest,
    ) -> Student:
        await self.get_by_id(section_id)

        student = await self.repo.get_student_by_id(request.student_id)
        if student is None:
            raise NotFound(ERROR_CODES.COURSE_SECTION.STUDENT_NOT_FOUND)

        enrollment = await self.repo.get_enrollment(
            student_id=request.student_id,
            section_id=section_id,
            include_cancel=True,
        )
        if enrollment is not None and not enrollment.is_cancel:
            raise AlreadyExists(ERROR_CODES.COURSE_SECTION.STUDENT_ALREADY_ENROLLED)

        if enrollment is not None and enrollment.is_cancel:
            await self.repo.restore_enrollment(enrollment)
        else:
            await self.repo.create_enrollment(
                student_id=request.student_id, section_id=section_id
            )

        refreshed = await self.repo.get_student_by_id(request.student_id)
        return refreshed if refreshed is not None else student

    async def remove_student_from_section(
        self, section_id: int, student_id: int
    ) -> None:
        await self.get_by_id(section_id)

        student = await self.repo.get_student_by_id(student_id)
        if student is None:
            raise NotFound(ERROR_CODES.COURSE_SECTION.STUDENT_NOT_FOUND)

        enrollment = await self.repo.get_enrollment(
            student_id=student_id,
            section_id=section_id,
            include_cancel=False,
        )
        if enrollment is None:
            raise Validation(
                message="Sinh viên chưa thuộc lớp tín chỉ này",
                error_code=ERROR_CODES.COURSE_SECTION.STUDENT_NOT_ENROLLED,
            )

        await self.repo.soft_delete_enrollment(enrollment)

    async def build_student_import_template(self, section_id: int) -> bytes:
        await self.get_by_id(section_id)

        wb = Workbook()
        ws = wb.active
        ws.title = "credit_class_students"
        ws.append(["Mã sinh viên"])
        ws.append(["22A1001D0043"])

        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)
        return stream.read()

    async def import_students_from_excel(
        self,
        section_id: int,
        file_content: bytes,
        filename: str | None = None,
    ) -> StudentImportResultResponse:
        await self.get_by_id(section_id)

        if not file_content:
            raise Validation(message="File Excel trống")

        self._validate_file_extension(filename)

        try:
            wb = load_workbook(filename=BytesIO(file_content), data_only=True)
        except Exception as exc:  # noqa: BLE001
            raise Validation(
                message="Không thể đọc file Excel. Vui lòng kiểm tra định dạng .xlsx"
            ) from exc

        ws = wb.active
        if ws.max_row < 2:
            raise Validation(message="File Excel không có dữ liệu sinh viên")

        raw_headers = [
            self._stringify_cell(cell)
            for cell in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
        ]
        header_index = self._build_header_index(raw_headers)

        if "student_code" not in header_index:
            raise Validation(message="Thiếu cột bắt buộc trong file mẫu: Mã sinh viên")

        errors: list[StudentImportErrorResponse] = []
        candidates: list[tuple[int, str, str]] = []
        seen_codes_in_file: set[str] = set()
        non_empty_rows = 0

        for row_idx, row_values in enumerate(
            ws.iter_rows(min_row=2, values_only=True),
            start=2,
        ):
            student_code_raw = self._stringify_cell(
                row_values[header_index["student_code"]]
            )

            if not any(self._stringify_cell(cell) for cell in row_values):
                continue

            non_empty_rows += 1

            if not student_code_raw:
                self._append_import_error(
                    errors,
                    row_idx,
                    "student_code",
                    "Mã sinh viên là bắt buộc",
                )
                continue

            code_key = student_code_raw.lower()
            if code_key in seen_codes_in_file:
                self._append_import_error(
                    errors,
                    row_idx,
                    "student_code",
                    "Mã sinh viên bị trùng trong file import",
                    student_code_raw,
                )
                continue

            seen_codes_in_file.add(code_key)
            candidates.append((row_idx, student_code_raw, code_key))

        imported_count = 0
        for row_idx, student_code_raw, _code_key in candidates:
            student = await self.repo.get_student_by_code_ci(student_code_raw)
            if student is None:
                self._append_import_error(
                    errors,
                    row_idx,
                    "student_code",
                    "Mã sinh viên không tồn tại trong hệ thống",
                    student_code_raw,
                )
                continue

            enrollment = await self.repo.get_enrollment(
                student_id=student.id,
                section_id=section_id,
                include_cancel=True,
            )

            if enrollment is not None and not enrollment.is_cancel:
                self._append_import_error(
                    errors,
                    row_idx,
                    "student_code",
                    "Sinh viên đã tồn tại trong lớp tín chỉ",
                    student_code_raw,
                )
                continue

            if enrollment is not None and enrollment.is_cancel:
                await self.repo.restore_enrollment(enrollment)
            else:
                await self.repo.create_enrollment(
                    student_id=student.id,
                    section_id=section_id,
                )
            imported_count += 1

        failed_count = len(errors)
        return StudentImportResultResponse(
            total_rows=non_empty_rows,
            imported_count=imported_count,
            failed_count=failed_count,
            errors=errors,
        )
