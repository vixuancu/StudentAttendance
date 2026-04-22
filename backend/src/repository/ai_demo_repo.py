from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.attendance import Attendance
from src.db.models.class_session import ClassSession
from src.db.models.course_section import CourseSection
from src.db.models.course import Course
from src.db.models.enrollment import Enrollment
from src.db.models.classroom import Classroom
from src.db.models.user import User
from src.db.models.student import Student
from src.db.models.student_face import StudentFace


class AIDemoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_active_student_faces(self) -> list[dict]:
        result = await self.db.execute(
            select(
                StudentFace.student_id,
                Student.student_code,
                Student.full_name,
                StudentFace.embedding,
            )
            .join(Student, Student.id == StudentFace.student_id)
            .where(Student.is_cancel.is_(False))
            .order_by(Student.id.asc(), StudentFace.id.asc())
        )

        rows = []
        for student_id, student_code, full_name, embedding in result.all():
            rows.append(
                {
                    "student_id": int(student_id),
                    "student_code": student_code,
                    "full_name": full_name,
                    "embedding": embedding,
                }
            )
        return rows

    async def fetch_student_faces_by_course_section(self, course_section_id: int) -> list[dict]:
        result = await self.db.execute(
            select(
                StudentFace.student_id,
                Student.student_code,
                Student.full_name,
                StudentFace.embedding,
            )
            .join(Student, Student.id == StudentFace.student_id)
            .join(
                Enrollment,
                (Enrollment.student_id == Student.id)
                & (Enrollment.course_section_id == course_section_id)
                & (Enrollment.is_cancel.is_(False)),
            )
            .where(Student.is_cancel.is_(False))
            .order_by(Student.id.asc(), StudentFace.id.asc())
        )

        rows = []
        for student_id, student_code, full_name, embedding in result.all():
            rows.append(
                {
                    "student_id": int(student_id),
                    "student_code": student_code,
                    "full_name": full_name,
                    "embedding": embedding,
                }
            )
        return rows

    async def get_class_session_detail(self, class_session_id: int) -> ClassSession | None:
        result = await self.db.execute(
            select(ClassSession)
            .options(
                selectinload(ClassSession.course_section).selectinload(CourseSection.course),
                selectinload(ClassSession.course_section).selectinload(CourseSection.user),
                selectinload(ClassSession.room),
            )
            .where(ClassSession.id == class_session_id, ClassSession.is_cancel.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_attendance_by_student_and_session(
        self,
        student_id: int,
        class_session_id: int,
        include_cancel: bool = False,
    ) -> Attendance | None:
        stmt = select(Attendance).where(
            Attendance.student_id == student_id,
            Attendance.class_session_id == class_session_id,
        ).order_by(Attendance.id.desc())
        if not include_cancel:
            stmt = stmt.where(Attendance.is_cancel.is_(False))

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_attendance(
        self,
        student_id: int,
        class_session_id: int,
        status: int,
        note: str | None = None,
    ) -> Attendance:
        item = Attendance(
            student_id=student_id,
            class_session_id=class_session_id,
            status=status,
            note=note,
            is_cancel=False,
        )
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def update_attendance(
        self,
        attendance: Attendance,
        status: int,
        note: str | None = None,
    ) -> Attendance:
        attendance.status = status
        attendance.note = note
        attendance.is_cancel = False
        await self.db.flush()
        await self.db.refresh(attendance)
        return attendance

    async def get_active_student_by_id(self, student_id: int) -> Student | None:
        result = await self.db.execute(
            select(Student).where(Student.id == student_id, Student.is_cancel.is_(False))
        )
        return result.scalar_one_or_none()

    async def add_student_face(self, student_id: int, image_url: str, embedding: list[float]) -> StudentFace:
        face = StudentFace(
            student_id=student_id,
            image_url=image_url,
            embedding=embedding,
        )
        self.db.add(face)
        await self.db.flush()
        await self.db.refresh(face)
        return face

    async def list_student_faces(self, student_id: int) -> list[StudentFace]:
        result = await self.db.execute(
            select(StudentFace)
            .where(StudentFace.student_id == student_id)
            .order_by(StudentFace.created_at.desc(), StudentFace.id.desc())
        )
        return list(result.scalars().all())
