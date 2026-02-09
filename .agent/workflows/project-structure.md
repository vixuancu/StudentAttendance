---
description: Quy tắc và cấu trúc dự án StudentAttendance - PHẢI ĐỌC trước khi code
---

# 📚 Kiến Trúc Dự Án StudentAttendance

## 1. TỔNG QUAN KIẾN TRÚC

Dự án sử dụng **Layered Architecture** với **Dependency Injection (DI)** và **Interface Abstraction**.

### 1.1 Luồng xử lý request

```
Client Request
   ↓
Routes (khai báo endpoint – KHÔNG có logic)
   ↓
Controller (điều phối mỏng – nhận request, gọi service, map DTO, xử lý HTTP)
   ↓
Service (business logic thuần – throw BusinessException, KHÔNG biết HTTP)
   ↓
Repository (data access – chỉ CRUD thuần)
   ↓
Database (PostgreSQL)
```

### 1.2 Trách nhiệm từng Layer

| Layer          | Nhiệm vụ                                                                          | KHÔNG được làm                                |
| -------------- | --------------------------------------------------------------------------------- | --------------------------------------------- |
| **Routes**     | Khai báo endpoint, khai báo path/query params, gọi Controller                     | Chứa bất kỳ logic nào                         |
| **Controller** | Nhận request → validate (Pydantic) → gọi Service → map Response DTO → HTTP status | Chứa business logic, gọi trực tiếp Repository |
| **Service**    | Business logic thuần, throw `BusinessException`                                   | Import FastAPI, biết về HTTP status code      |
| **Repository** | Truy vấn DB (CRUD), build filter/query                                            | Chứa logic nghiệp vụ, throw HTTP exception    |

### 1.3 Exception Flow

```
Repository   → có thể raise SQLAlchemy exceptions
Service      → catch + raise BusinessException (NotFoundException, AlreadyExistsException, ...)
Controller   → KHÔNG catch exception (để lan ra)
main.py      → Exception Handlers chuyển BusinessException → HTTP Response (404, 409, 422, 400)
```

> **Quy tắc vàng**: Service KHÔNG ĐƯỢC import FastAPI. Chỉ throw BusinessException.
> Controller KHÔNG catch exception. Exception handlers ở main.py lo việc convert → HTTP.

### 1.4 Dependency Injection

```
Routes → inject Controller (qua Depends)
Controller ← inject IService (interface)
Service ← inject IRepository (interface)
Repository ← inject AsyncSession
```

- **deps.py** đăng ký toàn bộ DI chain: `get_db → get_xxx_repo → get_xxx_service → get_xxx_controller`
- Mọi layer nhận **interface** (ABC), không nhận **concrete class**

---

## 2. CẤU TRÚC THƯ MỤC

```
backend/
├── alembic/                    # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry + Exception Handlers
│   ├── deps.py                 # DI Container – đăng ký dependencies
│   │
│   ├── config/
│   │   └── settings.py         # Pydantic Settings từ .env
│   │
│   ├── db/
│   │   ├── base.py             # Base, IDMixin, TimestampMixin
│   │   ├── session.py          # engine, async_session_factory, get_db
│   │   └── models/
│   │       ├── enums.py        # Enum types
│   │       ├── user.py         # User, Lecturer
│   │       ├── student.py      # Student
│   │       ├── course.py       # Course, CourseStudent, ClassSession
│   │       ├── attendance.py   # AttendanceRecord, AttendanceEvent
│   │       └── face_embedding.py
│   │
│   ├── dto/
│   │   ├── common.py           # BaseResponse, DataResponse, ListResponse, PaginationParams
│   │   ├── request/            # Pydantic models cho input
│   │   │   └── student_request.py
│   │   └── response/           # Pydantic models cho output
│   │       └── student_response.py
│   │
│   ├── repository/
│   │   ├── interfaces/         # ⭐ Repository Interfaces (ABC)
│   │   │   └── i_student_repo.py
│   │   ├── base.py             # BaseRepository (generic CRUD)
│   │   └── student_repo.py     # StudentRepository(BaseRepository, IStudentRepository)
│   │
│   ├── services/
│   │   ├── interfaces/         # ⭐ Service Interfaces (ABC)
│   │   │   └── i_student_service.py
│   │   └── student_service.py  # StudentService(IStudentService) – business logic
│   │
│   ├── controller/
│   │   └── student_controller.py  # Điều phối mỏng – map DTO
│   │
│   ├── routes/
│   │   ├── router.py           # Main router, include all v1 routes
│   │   └── v1/
│   │       └── student_routes.py  # Khai báo endpoint, gọi Controller
│   │
│   ├── middleware/
│   │   ├── auth.py
│   │   └── cors.py
│   │
│   └── utils/
│       ├── exceptions.py       # BusinessException, NotFoundException, AlreadyExistsException, ...
│       ├── datetime_utils.py
│       ├── file_utils.py
│       └── security.py
│
├── .env
├── .env.example
├── alembic.ini
└── requirements.txt
```

---

## 3. MẪU CODE CHI TIẾT

### 3.1 Business Exceptions (utils/exceptions.py)

```python
class BusinessException(Exception):
    """Base exception cho tất cả business errors"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class NotFoundException(BusinessException):
    def __init__(self, resource: str, identifier: str | int):
        message = f"{resource} với ID '{identifier}' không tồn tại"
        super().__init__(message, error_code="NOT_FOUND")

class AlreadyExistsException(BusinessException):
    def __init__(self, resource: str, field: str, value: str):
        message = f"{resource} với {field} '{value}' đã tồn tại"
        super().__init__(message, error_code="ALREADY_EXISTS")
```

### 3.2 Repository Interface (ABC)

```python
# src/repository/interfaces/i_student_repo.py
from abc import ABC, abstractmethod
from typing import Any, List, Optional
from src.db.models.student import Student

class IStudentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Student]: pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100,
                      filters: Optional[List[Any]] = None) -> List[Student]: pass

    @abstractmethod
    async def count(self, filters: Optional[List[Any]] = None) -> int: pass

    @abstractmethod
    async def create(self, data: dict) -> Student: pass

    @abstractmethod
    async def update(self, db_obj: Student, data: dict) -> Student: pass

    @abstractmethod
    async def delete(self, id: int) -> bool: pass

    @abstractmethod
    async def get_by_student_code(self, code: str) -> Optional[Student]: pass
```

### 3.3 Repository Implementation

```python
# src/repository/student_repo.py
from src.repository.base import BaseRepository
from src.repository.interfaces.i_student_repo import IStudentRepository
from src.db.models.student import Student

class StudentRepository(BaseRepository, IStudentRepository):
    """
    Kế thừa BaseRepository (generic CRUD) + implement IStudentRepository (contract).
    Chỉ viết thêm method đặc thù cho Student.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(Student, db)  # BaseRepository nhận model + session

    async def get_by_student_code(self, code: str) -> Optional[Student]:
        result = await self.db.execute(
            select(Student).where(Student.student_code == code)
        )
        return result.scalar_one_or_none()
```

### 3.4 Service Interface (ABC)

```python
# src/services/interfaces/i_student_service.py
from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from src.db.models.student import Student
from src.dto.common import PaginationParams
from src.dto.request.student_request import StudentCreateRequest, StudentUpdateRequest

class IStudentService(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Student: pass

    @abstractmethod
    async def get_students(self, pagination: PaginationParams,
                           search: Optional[str] = None,
                           class_code: Optional[str] = None) -> Tuple[List[Student], int]: pass

    @abstractmethod
    async def create(self, request: StudentCreateRequest) -> Student: pass

    @abstractmethod
    async def update(self, id: int, request: StudentUpdateRequest) -> Student: pass

    @abstractmethod
    async def delete(self, id: int) -> bool: pass
```

### 3.5 Service Implementation (BUSINESS LOGIC THUẦN)

```python
# src/services/student_service.py
# ❌ KHÔNG import FastAPI / HTTPException
# ✅ Chỉ throw BusinessException

from src.repository.interfaces.i_student_repo import IStudentRepository
from src.services.interfaces.i_student_service import IStudentService
from src.utils.exceptions import NotFoundException, AlreadyExistsException

class StudentService(IStudentService):
    def __init__(self, repo: IStudentRepository):
        self.repo = repo  # Inject interface

    async def get_by_id(self, id: int) -> Student:
        student = await self.repo.get_by_id(id)
        if not student:
            raise NotFoundException(resource="Sinh viên", identifier=id)
        return student

    async def create(self, request: StudentCreateRequest) -> Student:
        existing = await self.repo.get_by_student_code(request.student_code)
        if existing:
            raise AlreadyExistsException(
                resource="Sinh viên", field="student_code", value=request.student_code
            )
        return await self.repo.create(request.model_dump())
```

### 3.6 Controller (ĐIỀU PHỐI MỎNG)

```python
# src/controller/student_controller.py
# Nhiệm vụ:
#   ✅ Nhận request từ route
#   ✅ Gọi service
#   ✅ Map kết quả → Response DTO
#   ❌ KHÔNG chứa business logic

from src.services.interfaces.i_student_service import IStudentService
from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.response.student_response import StudentResponse

class StudentController:
    def __init__(self, service: IStudentService):
        self.service = service

    async def get_student(self, id: int) -> DataResponse[StudentResponse]:
        student = await self.service.get_by_id(id)
        return DataResponse(
            data=StudentResponse.model_validate(student),
            message="Lấy thông tin sinh viên thành công",
        )

    async def create_student(self, request: StudentCreateRequest) -> DataResponse[StudentResponse]:
        student = await self.service.create(request)
        return DataResponse(
            data=StudentResponse.model_validate(student),
            message="Tạo sinh viên thành công",
        )
```

### 3.7 DI Container (deps.py)

```python
# src/deps.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db

# ============ STUDENT ============
from src.repository.student_repo import StudentRepository
from src.services.student_service import StudentService
from src.controller.student_controller import StudentController

def get_student_repo(db: AsyncSession = Depends(get_db)) -> IStudentRepository:
    return StudentRepository(db)

def get_student_service(repo: IStudentRepository = Depends(get_student_repo)) -> IStudentService:
    return StudentService(repo)

def get_student_controller(service: IStudentService = Depends(get_student_service)) -> StudentController:
    return StudentController(service)
```

### 3.8 Routes (THIN LAYER)

```python
# src/routes/v1/student_routes.py
# ❌ KHÔNG chứa logic – chỉ khai báo endpoint và gọi controller

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/{student_id}", response_model=DataResponse[StudentResponse])
async def get_student(
    student_id: int,
    ctrl: StudentController = Depends(get_student_controller),
):
    return await ctrl.get_student(student_id)
```

### 3.9 Exception Handlers (main.py)

```python
# src/main.py
# Chuyển BusinessException → HTTP Response tại đây

@app.exception_handler(NotFoundException)
async def not_found_handler(request, exc: NotFoundException):
    return JSONResponse(status_code=404, content={
        "success": False, "message": exc.message, "error_code": exc.error_code,
    })

@app.exception_handler(AlreadyExistsException)
async def already_exists_handler(request, exc: AlreadyExistsException):
    return JSONResponse(status_code=409, content={
        "success": False, "message": exc.message, "error_code": exc.error_code,
    })
```

---

## 4. QUY TẮC IMPORT

```python
# ✅ ĐÚNG – import từ src
from src.config.settings import settings
from src.db.models.student import Student
from src.repository.interfaces.i_student_repo import IStudentRepository
from src.utils.exceptions import NotFoundException

# ❌ SAI – không dùng backend.src
from backend.src.config.settings import settings
```

---

## 5. THỨ TỰ TẠO API MỚI (Checklist)

1. `src/repository/interfaces/i_xxx_repo.py` – Interface Repository (ABC)
2. `src/repository/xxx_repo.py` – Concrete Repository (kế thừa BaseRepository + IRepo)
3. `src/services/interfaces/i_xxx_service.py` – Interface Service (ABC)
4. `src/services/xxx_service.py` – Concrete Service (throw BusinessException)
5. `src/controller/xxx_controller.py` – Controller (map DTO, gọi service)
6. `src/deps.py` – Đăng ký DI chain: repo → service → controller
7. `src/routes/v1/xxx_routes.py` – Routes (thin, gọi controller)
8. `src/routes/router.py` – Include router mới

---

## 6. NGUYÊN TẮC QUAN TRỌNG

| Nguyên tắc                             | Mô tả                                                   |
| -------------------------------------- | ------------------------------------------------------- |
| **Service không biết HTTP**            | Không import FastAPI, không throw HTTPException         |
| **BusinessException → HTTP ở main.py** | Exception handlers convert exception → HTTP status code |
| **Controller không có business logic** | Chỉ gọi service + map DTO                               |
| **Repository kế thừa BaseRepository**  | Generic CRUD có sẵn, chỉ viết thêm method đặc thù       |
| **DI qua interface**                   | Inject IRepository, IService – không inject concrete    |
| **Routes là thin layer**               | Chỉ khai báo endpoint, Depends controller, trả kết quả  |
