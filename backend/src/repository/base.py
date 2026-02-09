from typing import Any, List, Optional, TypeVar
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.base import Base

ModelType = TypeVar("ModelType", bound=Base) # tạo kiểu tổng quát cho các model kế thừa từ Base

class BaseRepository:
    """
    Generic repository với các CRUD operations cơ bản.
    Kế thừa class này cho từng entity.
    """
    # Khởi tạo với model cụ thể và phiên làm việc DB
    def __init__(self,model: type[ModelType],db: AsyncSession): 
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Lấy bản ghi theo ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none() # trả về một bản ghi hoặc None nếu không tìm thấy
    
    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            filters: Optional[List[Any]] = None
    ) -> List[ModelType] :
        """ Lấy danh sách bản ghi với pagination và filter"""
        query = select(self.model)
    
        if filters:
            for f in filters:
                query = query.where(f)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()) # trả về danh sách bản ghi
    
    async def count(
            self,
            filters: Optional[List[Any]] = None
    )-> int:
        """Đếm số bản ghi với filter."""
        query = select(func.count(self.model.id))

        if filters:
            for f in filters:
                query = query.where(f)
        result = await self.db.execute(query)
        return result.scalar_one() or 0 
    
    async def create(self, obj_data: dict) -> ModelType:
        """tạo bản ghi mới."""
        db_obj = self.model(**obj_data) # tạo instance của model
        self.db.add(db_obj)
        await self.db.flush() # ghi vào DB
        await self.db.refresh(db_obj) # làm mới instance với dữ liệu từ DB
        return db_obj
    
    async def update(self, db_obj: ModelType, update_data: dict) -> ModelType:
        """ Cập nhật bản ghi"""
        for field, value in update_data.items():
            if value is not None:
                setattr(db_obj, field, value) # cập nhật trường nếu giá trị không phải None
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: int) -> bool:
        """Xóa bản ghi theo ID"""
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0  # trả về True nếu có bản ghi bị xóa



