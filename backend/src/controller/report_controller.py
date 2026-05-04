from typing import Optional, List
from datetime import date

from src.dto.common import DataResponse
from src.db.models.user import User
from src.services.interfaces.i_report_service import IReportService
from src.dto.response.report_response import (
    ReportStatsResponse,
    ReportOverviewResponse,
    WeeklyTrendItem,
    ClassSummaryItem,
    PaginatedReportDetailResponse,
)


class ReportController:
    def __init__(self, service: IReportService):
        self.service = service

    async def get_report_stats(
        self,
        course_section_id: Optional[int],
        from_date: Optional[date],
        to_date: Optional[date],
        current_user: User,
    ) -> DataResponse[ReportStatsResponse]:
        data = await self.service.get_report_stats(
            course_section_id, from_date, to_date
        )
        return DataResponse(data=data, message="Lấy dữ liệu thống kê thành công")

    async def get_overview(
        self, current_user: User
    ) -> DataResponse[ReportOverviewResponse]:
        data = await self.service.get_overview()
        return DataResponse(data=data, message="Lấy dữ liệu tổng quan thành công")

    async def get_weekly_trend(
        self,
        course_section_id: Optional[int],
        from_date: Optional[date],
        to_date: Optional[date],
        current_user: User,
    ) -> DataResponse[List[WeeklyTrendItem]]:
        data = await self.service.get_weekly_trend(
            course_section_id, from_date, to_date
        )
        return DataResponse(data=data, message="Lấy biểu đồ xu hướng tuần thành công")

    async def get_class_summary(
        self, from_date: Optional[date], to_date: Optional[date], current_user: User
    ) -> DataResponse[List[ClassSummaryItem]]:
        data = await self.service.get_class_summary(from_date, to_date)
        return DataResponse(data=data, message="Lấy thống kê theo lớp thành công")

    async def get_report_details(
        self,
        course_section_id: Optional[int],
        from_date: Optional[date],
        to_date: Optional[date],
        page: int,
        per_page: int,
        current_user: User,
    ) -> DataResponse[PaginatedReportDetailResponse]:
        data = await self.service.get_report_details(
            course_section_id, from_date, to_date, page, per_page
        )
        return DataResponse(data=data, message="Lấy chi tiết điểm danh thành công")
