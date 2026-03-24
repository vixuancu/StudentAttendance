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
from src.repository.interfaces.i_student_face_repo import IStudentFaceRepository
from src.repository.student_face_repo import StudentFaceRepository

from src.services.interfaces.i_student_service import IStudentService
from src.services.student_service import StudentService
from src.services.interfaces.i_student_face_service import IStudentFaceService
from src.services.student_face_service import StudentFaceService

from src.controller.student_controller import StudentController
from src.controller.student_face_controller import StudentFaceController


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


def get_student_face_repo(
    db: AsyncSession = Depends(get_db),
) -> IStudentFaceRepository:
    return StudentFaceRepository(db)


def get_student_face_service(
    student_repo: IStudentRepository = Depends(get_student_repo),
    face_repo: IStudentFaceRepository = Depends(get_student_face_repo),
) -> IStudentFaceService:
    return StudentFaceService(student_repo, face_repo)


def get_student_face_controller(
    service: IStudentFaceService = Depends(get_student_face_service),
) -> StudentFaceController:
    return StudentFaceController(service)


# ===================== AUTH ===================== #
from src.repository.interfaces.i_user_repo import IUserRepository
from src.repository.user_repo import UserRepository

from src.services.interfaces.i_auth_service import IAuthService
from src.services.auth_service import AuthService
from src.services.interfaces.i_mail_provider import IMailProvider
from src.services.mail_provider import create_mail_provider

from src.controller.auth_controller import AuthController
from src.controller.account_controller import AccountController
from src.services.interfaces.i_account_service import IAccountService
from src.services.account_service import AccountService


def get_user_repo(
    db: AsyncSession = Depends(get_db),
) -> IUserRepository:
    return UserRepository(db)


def get_auth_service(
    user_repo: IUserRepository = Depends(get_user_repo),
) -> IAuthService:
    return AuthService(user_repo)


def get_auth_controller(
    service: IAuthService = Depends(get_auth_service),
) -> AuthController:
    return AuthController(service)


def get_mail_provider() -> IMailProvider:
    return create_mail_provider()


# ===================== ACCOUNT ===================== #


def get_account_service(
    user_repo: IUserRepository = Depends(get_user_repo),
) -> IAccountService:
    return AccountService(user_repo)


def get_account_controller(
    service: IAccountService = Depends(get_account_service),
) -> AccountController:
    return AccountController(service)


# ===================== CAMERA ===================== #
from src.repository.interfaces.i_camera_repo import ICameraRepository
from src.repository.camera_repo import CameraRepository

from src.services.interfaces.i_camera_service import ICameraService
from src.services.camera_service import CameraService

from src.controller.camera_controller import CameraController

def get_camera_repo(
    db: AsyncSession = Depends(get_db)
) -> ICameraRepository:
    return CameraRepository(db)

def get_camera_service(
    camera_repo: ICameraRepository = Depends(get_camera_repo),
) -> ICameraService:
    return CameraService(camera_repo)
    
def get_camera_controller(
    service: ICameraService = Depends(get_camera_service),
) -> CameraController:
    return CameraController(service)
