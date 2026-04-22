from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.attendance import Attendance
from src.db.models.class_session import ClassSession
from src.repository.interfaces.i_attendance_repo import IAttendanceRepository

class AttendanceRepository(IAttendanceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_attendances_by_course_section_and_date_range(
        self,
        course_section_id: int,
        from_date: Optional[object],
        to_date: Optional[object]
    ) -> List[Attendance]:
        stmt = select(Attendance).join(ClassSession).where(
            ClassSession.course_section_id == course_section_id,
            Attendance.is_cancel == False,
            ClassSession.is_cancel == False
        ).options(selectinload(Attendance.student), selectinload(Attendance.class_session))

        if from_date:
            stmt = stmt.where(ClassSession.session_date >= from_date)
        if to_date:
            stmt = stmt.where(ClassSession.session_date <= to_date)
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_class_sessions_by_course_section_and_date_range(
        self,
        course_section_id: int,
        from_date: Optional[object],
        to_date: Optional[object]
    ) -> List[ClassSession]:
        stmt = select(ClassSession).where(
            ClassSession.course_section_id == course_section_id,
            ClassSession.is_cancel == False
        ).order_by(ClassSession.session_date.asc())

        if from_date:
            stmt = stmt.where(ClassSession.session_date >= from_date)
        if to_date:
            stmt = stmt.where(ClassSession.session_date <= to_date)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_class_session_by_id(
        self,
        class_session_id: int
    ) -> Optional[ClassSession]:
        stmt = select(ClassSession).where(ClassSession.id == class_session_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_attendance_by_student_and_session(
        self, 
        student_id: int, 
        class_session_id: int
    ) -> Optional[Attendance]:
        stmt = select(Attendance).where(
            Attendance.student_id == student_id,
            Attendance.class_session_id == class_session_id,
            Attendance.is_cancel == False
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_attendance(
        self, 
        student_id: int, 
        class_session_id: int, 
        status: int, 
        note: Optional[str]
    ) -> Attendance:
        attendance = Attendance(
            student_id=student_id,
            class_session_id=class_session_id,
            status=status,
            note=note,
            is_cancel=False
        )
        self.session.add(attendance)
        await self.session.commit()
        await self.session.refresh(attendance)
        return attendance

    async def update_attendance(
        self, 
        attendance: Attendance, 
        status: Optional[int], 
        note: Optional[str]
    ) -> Attendance:
        attendance.status = status
        attendance.note = note
        await self.session.commit()
        await self.session.refresh(attendance)
        return attendance

    async def soft_delete_attendance(
        self,
        attendance: Attendance
    ) -> None:
        attendance.is_cancel = True
        attendance.status = None
        attendance.note = None
        await self.session.commit()
