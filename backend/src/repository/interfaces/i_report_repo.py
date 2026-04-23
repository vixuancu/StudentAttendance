from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from datetime import date

class IReportRepository(ABC):
    @abstractmethod
    async def get_report_stats(
        self,
        course_section_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, int]:
        pass

    @abstractmethod
    async def get_weekly_trend(
        self,
        course_section_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_class_summary(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_report_details(
        self,
        course_section_id: Optional[int] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        page: int = 1,
        per_page: int = 10
    ) -> Tuple[List[Any], int]:
        pass
