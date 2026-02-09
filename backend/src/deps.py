"""
DI Container – Đăng ký và inject tất cả dependencies.
Mỗi module (student, user, …) có 3 factory: repo → service → controller.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db

# ===================== STUDENT ===================== #
from src.repository.interfaces.i_student_repo import IStudentRepository
from src.repository.student_repo import StudentRepository

from src.services.interfaces.i_student_service import IStudentService
from src.services.student_service import StudentService

from src.controller.student_controller import StudentController


def get_student_repo(
    db: AsyncSession = Depends(get_db),
) -> IStudentRepository:
    return StudentRepository(db)


def get_student_service(
    repo: IStudentRepository = Depends(get_student_repo),
) -> IStudentService:
    return StudentService(repo)


def get_student_controller(
    service: IStudentService = Depends(get_student_service),
) -> StudentController:
    return StudentController(service)


# ===================== USER ===================== #
# def get_user_repo(db: AsyncSession = Depends(get_db)) -> IUserRepository:
#     return UserRepository(db)
#
# def get_user_service(repo: IUserRepository = Depends(get_user_repo)) -> IUserService:
#     return UserService(repo)
#
# def get_user_controller(service: IUserService = Depends(get_user_service)) -> UserController:
#     return UserController(service)
