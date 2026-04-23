from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from src.dto.response.report_response import (
    ReportStatsResponse,
    WeeklyTrendItem,
    ClassSummaryItem,
    PaginatedReportDetailResponse
)

class IReportService(ABC):
    @abstractmethod
    async def get_report_stats(
        self,
        course_section_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> ReportStatsResponse:
        pass

    @abstractmethod
    async def get_weekly_trend(
        self,
        course_section_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[WeeklyTrendItem]:
        pass

    @abstractmethod
    async def get_class_summary(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[ClassSummaryItem]:
        pass

    @abstractmethod
    async def get_report_details(
        self,
        course_section_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        page: int = 1,
        per_page: int = 10
    ) -> PaginatedReportDetailResponse:
        pass
