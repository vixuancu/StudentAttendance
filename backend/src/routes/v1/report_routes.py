from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, Query

from src.controller.report_controller import ReportController
from src.db.models.user import User
from src.dto.common import DataResponse
from src.dto.response.report_response import (
    ReportStatsResponse,
    WeeklyTrendItem,
    ClassSummaryItem,
    PaginatedReportDetailResponse
)
from src.middleware.auth import require_roles
from src.deps import get_report_controller

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/stats", response_model=DataResponse[ReportStatsResponse])
async def get_report_stats(
    course_section_id: Optional[int] = Query(None, description="ID của lớp tín chỉ"),
    from_date: Optional[date] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
    current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: ReportController = Depends(get_report_controller)
):
    return await ctrl.get_report_stats(course_section_id, from_date, to_date, current_user)

@router.get("/weekly-trend", response_model=DataResponse[List[WeeklyTrendItem]])
async def get_weekly_trend(
    course_section_id: Optional[int] = Query(None, description="ID của lớp tín chỉ"),
    from_date: Optional[date] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
    current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: ReportController = Depends(get_report_controller)
):
    return await ctrl.get_weekly_trend(course_section_id, from_date, to_date, current_user)

@router.get("/class-summary", response_model=DataResponse[List[ClassSummaryItem]])
async def get_class_summary(
    from_date: Optional[date] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
    current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: ReportController = Depends(get_report_controller)
):
    return await ctrl.get_class_summary(from_date, to_date, current_user)

@router.get("/details", response_model=DataResponse[PaginatedReportDetailResponse])
async def get_report_details(
    course_section_id: Optional[int] = Query(None, description="ID của lớp tín chỉ"),
    from_date: Optional[date] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: ReportController = Depends(get_report_controller)
):
    return await ctrl.get_report_details(course_section_id, from_date, to_date, page, per_page, current_user)
