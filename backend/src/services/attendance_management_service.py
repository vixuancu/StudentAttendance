from typing import Optional
from datetime import date

from src.db.models.user import User
from src.repository.interfaces.i_attendance_repo import IAttendanceRepository
from src.repository.interfaces.i_course_section_repo import ICourseSectionRepository
from src.services.interfaces.i_attendance_management_service import IAttendanceManagementService
from src.dto.request.attendance_management_request import AttendanceUpdateCellRequest
from src.dto.response.attendance_management_response import (
    AttendanceMatrixResponse,
    StudentAttendanceMatrixResponse,
    AttendanceRecordResponse,
)
from src.utils.exceptions import ForbiddenException, NotFoundException

class AttendanceManagementService(IAttendanceManagementService):
    def __init__(
        self, 
        attendance_repo: IAttendanceRepository,
        course_section_repo: ICourseSectionRepository
    ):
        self.attendance_repo = attendance_repo
        self.course_section_repo = course_section_repo

    async def _check_permission(self, course_section_id: int, current_user: User):
        role_name = current_user.role.role_name if hasattr(current_user, 'role') and current_user.role else None
        
        # admin and giao_vu have full access
        if role_name in ["admin", "giao_vu"]:
            return
            
        course_section = await self.course_section_repo.get_by_id(course_section_id)
        if not course_section:
            raise NotFoundException("Lớp tín chỉ không tồn tại")
            
        if role_name == "giang_vien" and int(course_section.user_id) != int(current_user.id):
            raise ForbiddenException("Giảng viên chỉ được xem hoặc chỉnh sửa lớp mình phụ trách")

    async def get_attendance_matrix(
        self,
        course_section_id: int,
        from_date: Optional[date],
        to_date: Optional[date],
        current_user: User
    ) -> AttendanceMatrixResponse:
        await self._check_permission(course_section_id, current_user)

        enrolled_students = await self.course_section_repo.list_enrolled_students(
            course_section_id, skip=0, limit=10000, search=None
        )

        attendances = await self.attendance_repo.get_attendances_by_course_section_and_date_range(
            course_section_id, from_date, to_date
        )
        
        sessions = await self.attendance_repo.get_class_sessions_by_course_section_and_date_range(
            course_section_id, from_date, to_date
        )

        student_map = {}
        for student in enrolled_students:
            student_map[student.id] = {
                "student_id": student.id,
                "student_code": student.student_code,
                "full_name": student.full_name,
                "records_map": {}
            }
        
        for attendance in attendances:
            student = attendance.student
            if not student:
                 continue
                 
            student_id = student.id
            if student_id not in student_map:
                student_map[student_id] = {
                    "student_id": student.id,
                    "student_code": student.student_code,
                    "full_name": student.full_name,
                    "records_map": {}
                }
                
            student_map[student_id]["records_map"][attendance.class_session_id] = AttendanceRecordResponse(
                id=attendance.id,
                class_session_id=attendance.class_session_id,
                status=attendance.status,
                note=attendance.note,
                session_date=attendance.class_session.session_date,
                attendance_created_at=attendance.created_at,
            )

        students_matrix = []
        for sid, sdata in student_map.items():
            records = []
            for session in sessions:
                record = sdata["records_map"].get(session.id)
                if record:
                    records.append(record)
                else:
                    # Provide an empty record for sessions they haven't been marked for yet
                    records.append(AttendanceRecordResponse(
                        id=None,
                        class_session_id=session.id,
                        status=None,
                        note=None,
                        session_date=session.session_date,
                        attendance_created_at=None,
                    ))
            
            # Sort by session date just in case
            records.sort(key=lambda x: x.session_date)
                    
            students_matrix.append(StudentAttendanceMatrixResponse(
                student_id=sdata["student_id"],
                student_code=sdata["student_code"],
                full_name=sdata["full_name"],
                records=records
            ))
            
        students_matrix.sort(key=lambda x: x.student_code)

        return AttendanceMatrixResponse(
            course_section_id=course_section_id,
            students=students_matrix,
            total_sessions=len(sessions)
        )

    async def update_attendance_cell(
        self,
        request: AttendanceUpdateCellRequest,
        current_user: User
    ) -> dict:
        
        session = await self.attendance_repo.get_class_session_by_id(request.class_session_id)
        if not session or session.is_cancel:
            raise NotFoundException("Buổi học không tồn tại hoặc đã bị hủy")
            
        await self._check_permission(session.course_section_id, current_user)
        
        existing = await self.attendance_repo.get_attendance_by_student_and_session(
            request.student_id, request.class_session_id
        )

        if request.status is None:
            if existing:
                await self.attendance_repo.soft_delete_attendance(existing)
            return {
                "id": None,
                "student_id": request.student_id,
                "class_session_id": request.class_session_id,
                "status": None,
                "note": None
            }
        
        if existing:
            attendance = await self.attendance_repo.update_attendance(
                existing, request.status, request.note
            )
        else:
            attendance = await self.attendance_repo.create_attendance(
                request.student_id, request.class_session_id, request.status, request.note
            )
            
        return {
            "id": attendance.id,
            "student_id": attendance.student_id,
            "class_session_id": attendance.class_session_id,
            "status": attendance.status,
            "note": attendance.note
        }
