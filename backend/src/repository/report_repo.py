from typing import List, Optional, Tuple, Dict, Any
from datetime import date, timedelta
from sqlalchemy import select, func, case, distinct, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.attendance import Attendance
from src.db.models.class_session import ClassSession
from src.db.models.course_section import CourseSection
from src.db.models.course import Course
from src.db.models.student import Student
from src.db.models.enums import AttendanceStatus
from src.repository.interfaces.i_report_repo import IReportRepository

class ReportRepository(IReportRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_report_stats(
        self,
        course_section_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, int]:
        
        # Build base conditions for sessions
        session_conds = [ClassSession.is_cancel == False]
        if course_section_id:
            session_conds.append(ClassSession.course_section_id == course_section_id)
        if from_date:
            session_conds.append(func.date(ClassSession.session_date) >= from_date)
        if to_date:
            session_conds.append(func.date(ClassSession.session_date) <= to_date)
            
        # We need to count attendance statuses. 
        # Since not all expected records might exist in attendance table (some might not have been marked yet),
        # or we might just aggregate over existing attendance records. 
        # Typically, attendance stats are aggregated over existing attendance records.
        # But for 'vang' it could be missing records if default isn't inserted. Let's assume they are inserted or we count existing.
        # Assuming existing records only for stats:
        
        stmt = select(
            func.count(Attendance.id).label('total'),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label('co_mat'),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label('tre'),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label('vang')
        ).select_from(Attendance).join(ClassSession).where(
            Attendance.is_cancel == False,
            *session_conds
        )
        
        result = await self.session.execute(stmt)
        row = result.first()
        
        return {
            "total_records": int(row.total) if row and row.total else 0,
            "co_mat": int(row.co_mat) if row and row.co_mat else 0,
            "tre": int(row.tre) if row and row.tre else 0,
            "vang": int(row.vang) if row and row.vang else 0
        }

    async def get_weekly_trend(
        self,
        course_section_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        
        session_conds = [ClassSession.is_cancel == False]
        if course_section_id:
            session_conds.append(ClassSession.course_section_id == course_section_id)
        if from_date:
            session_conds.append(func.date(ClassSession.session_date) >= from_date)
        if to_date:
            session_conds.append(func.date(ClassSession.session_date) <= to_date)
            
        # Extract week/year or ISO week from session date
        # PostgreSQL/MySQL specific. For simplicity, let's group by week. SQLite uses strftime.
        # It's better to fetch records and aggregate in python if DB agnostic, or use a general group by.
        # Let's aggregate in python to avoid dialect issues.
        
        stmt = select(
            ClassSession.session_date,
            Attendance.status
        ).select_from(Attendance).join(ClassSession).where(
            Attendance.is_cancel == False,
            *session_conds
        ).order_by(ClassSession.session_date.asc())
        
        result = await self.session.execute(stmt)
        records = result.all()
        
        # Aggregate in Python
        from collections import defaultdict
        
        weeks_data = defaultdict(lambda: {"total": 0, "co_mat": 0, "tre": 0, "vang": 0, "start_date": None})
        
        for r in records:
            s_date = r.session_date.date() if hasattr(r.session_date, 'date') else r.session_date
            # Get Monday of the week
            week_start = s_date - timedelta(days=s_date.weekday())
            week_key = week_start.strftime("%Y-%m-%d")
            
            weeks_data[week_key]["total"] += 1
            if r.status == AttendanceStatus.PRESENT:
                weeks_data[week_key]["co_mat"] += 1
            elif r.status == AttendanceStatus.LATE:
                weeks_data[week_key]["tre"] += 1
            elif r.status == AttendanceStatus.ABSENT:
                weeks_data[week_key]["vang"] += 1
            weeks_data[week_key]["start_date"] = week_key
            
        # Sort and format
        sorted_weeks = sorted(weeks_data.items())
        res = []
        for i, (key, data) in enumerate(sorted_weeks):
            total = data["total"]
            if total > 0:
                res.append({
                    "week_label": f"Tuần {i+1}",
                    "week_start": data["start_date"],
                    "co_mat": round((data["co_mat"] / total) * 100, 1),
                    "tre": round((data["tre"] / total) * 100, 1),
                    "vang": round((data["vang"] / total) * 100, 1)
                })
        
        return res

    async def get_class_summary(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        
        session_conds = [ClassSession.is_cancel == False]
        if from_date:
            session_conds.append(func.date(ClassSession.session_date) >= from_date)
        if to_date:
            session_conds.append(func.date(ClassSession.session_date) <= to_date)
            
        stmt = select(
            CourseSection.id.label('course_section_id'),
            CourseSection.name.label('course_section_name'),
            Course.course_name.label('course_name'),
            func.count(Attendance.id).label('total'),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label('co_mat')
        ).select_from(CourseSection).join(Course).join(ClassSession).outerjoin(
            Attendance, and_(Attendance.class_session_id == ClassSession.id, Attendance.is_cancel == False)
        ).where(
            CourseSection.is_cancel == False,
            *session_conds
        ).group_by(
            CourseSection.id, CourseSection.name, Course.course_name
        )
        
        result = await self.session.execute(stmt)
        rows = result.all()
        
        res = []
        for r in rows:
            total = int(r.total) if r.total else 0
            co_mat = int(r.co_mat) if r.co_mat else 0
            rate = round((co_mat / total) * 100, 1) if total > 0 else 0.0
            res.append({
                "course_section_id": r.course_section_id,
                "course_section_name": r.course_section_name,
                "course_name": r.course_name,
                "attendance_rate": rate
            })
            
        return res

    async def get_report_details(
        self,
        course_section_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        page: int = 1,
        per_page: int = 10
    ) -> Tuple[List[Any], int]:
        
        # Base query to find all combinations of student & session
        # If we only show existing attendances, we just query Attendance.
        # Let's query Attendance.
        
        session_conds = [ClassSession.is_cancel == False]
        if course_section_id:
            session_conds.append(ClassSession.course_section_id == course_section_id)
        if from_date:
            session_conds.append(func.date(ClassSession.session_date) >= from_date)
        if to_date:
            session_conds.append(func.date(ClassSession.session_date) <= to_date)
            
        base_stmt = select(Attendance).join(ClassSession).where(
            Attendance.is_cancel == False,
            *session_conds
        )
        
        # Count total
        count_stmt = select(func.count()).select_from(Attendance).join(ClassSession).where(
            Attendance.is_cancel == False,
            *session_conds
        )
        count_res = await self.session.execute(count_stmt)
        total = count_res.scalar() or 0
        
        # Fetch page
        offset = (page - 1) * per_page
        stmt = base_stmt.options(
            selectinload(Attendance.student),
            selectinload(Attendance.class_session).selectinload(ClassSession.course_section).selectinload(CourseSection.course)
        ).order_by(ClassSession.session_date.desc(), Attendance.id.asc()).offset(offset).limit(per_page)
        
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        
        return list(records), total
