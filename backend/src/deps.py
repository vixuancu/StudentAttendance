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
from src.repository.interfaces.i_administrative_class_repo import (
    IAdministrativeClassRepository,
)
from src.repository.administrative_class_repo import AdministrativeClassRepository
from src.services.interfaces.i_administrative_class_service import (
    IAdministrativeClassService,
)
from src.services.administrative_class_service import AdministrativeClassService
from src.controller.administrative_class_controller import AdministrativeClassController
from src.repository.interfaces.i_course_repo import ICourseRepository
from src.repository.course_repo import CourseRepository
from src.services.interfaces.i_course_service import ICourseService
from src.services.course_service import CourseService
from src.controller.course_controller import CourseController
from src.repository.interfaces.i_course_section_repo import ICourseSectionRepository
from src.repository.course_section_repo import CourseSectionRepository
from src.services.interfaces.i_course_section_service import ICourseSectionService
from src.services.course_section_service import CourseSectionService
from src.controller.course_section_controller import CourseSectionController


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


def get_administrative_class_repo(
    db: AsyncSession = Depends(get_db),
) -> IAdministrativeClassRepository:
    return AdministrativeClassRepository(db)


def get_administrative_class_service(
    repo: IAdministrativeClassRepository = Depends(get_administrative_class_repo),
) -> IAdministrativeClassService:
    return AdministrativeClassService(repo)


def get_administrative_class_controller(
    service: IAdministrativeClassService = Depends(get_administrative_class_service),
) -> AdministrativeClassController:
    return AdministrativeClassController(service)


def get_course_repo(
    db: AsyncSession = Depends(get_db),
) -> ICourseRepository:
    return CourseRepository(db)


def get_course_service(
    repo: ICourseRepository = Depends(get_course_repo),
) -> ICourseService:
    return CourseService(repo)


def get_course_controller(
    service: ICourseService = Depends(get_course_service),
) -> CourseController:
    return CourseController(service)


def get_course_section_repo(
    db: AsyncSession = Depends(get_db),
) -> ICourseSectionRepository:
    return CourseSectionRepository(db)


def get_course_section_service(
    repo: ICourseSectionRepository = Depends(get_course_section_repo),
) -> ICourseSectionService:
    return CourseSectionService(repo)


def get_course_section_controller(
    service: ICourseSectionService = Depends(get_course_section_service),
) -> CourseSectionController:
    return CourseSectionController(service)


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
from src.repository.interfaces.i_classroom_repo import IClassroomRepository
from src.repository.classroom_repo import ClassroomRepository
from src.services.interfaces.i_camera_service import ICameraService
from src.services.camera_service import CameraService

from src.controller.camera_controller import CameraController


def get_camera_repo(db: AsyncSession = Depends(get_db)) -> ICameraRepository:
    return CameraRepository(db)


def get_classroom_repo(db: AsyncSession = Depends(get_db)) -> IClassroomRepository:
    return ClassroomRepository(db)


def get_camera_service(
    camera_repo: ICameraRepository = Depends(get_camera_repo),
    classroom_repo: IClassroomRepository = Depends(get_classroom_repo),
) -> ICameraService:
    return CameraService(camera_repo, classroom_repo)


def get_camera_controller(
    service: ICameraService = Depends(get_camera_service),
) -> CameraController:
    return CameraController(service)


# ===================== ATTENDANCE MANAGEMENT ===================== #
from src.repository.interfaces.i_attendance_repo import IAttendanceRepository
from src.repository.attendance_repo import AttendanceRepository
from src.services.interfaces.i_attendance_management_service import IAttendanceManagementService
from src.services.attendance_management_service import AttendanceManagementService
from src.controller.attendance_management_controller import AttendanceManagementController

def get_attendance_repo(db: AsyncSession = Depends(get_db)) -> IAttendanceRepository:
    return AttendanceRepository(db)

def get_attendance_management_service(
    attendance_repo: IAttendanceRepository = Depends(get_attendance_repo),
    course_section_repo: ICourseSectionRepository = Depends(get_course_section_repo),
) -> IAttendanceManagementService:
    return AttendanceManagementService(attendance_repo, course_section_repo)

def get_attendance_management_controller(
    service: IAttendanceManagementService = Depends(get_attendance_management_service),
) -> AttendanceManagementController:
    return AttendanceManagementController(service)

# ==================== CLASSROOM ==================== #


from src.services.interfaces.i_classroom_service import IClassroomService
from src.services.classroom_service import ClassroomService

from src.controller.classroom_controller import ClassroomController


def get_classroom_service(
    classroom_repo: IClassroomRepository = Depends(get_classroom_repo),
    camera_repo: ICameraRepository = Depends(get_camera_repo),
) -> IClassroomService:
    return ClassroomService(classroom_repo, camera_repo)


def get_classroom_controller(
    service: IClassroomService = Depends(get_classroom_service),
) -> ClassroomController:
    return ClassroomController(service)


# ===================== AI DEMO ATTENDANCE ===================== #
from src.repository.ai_demo_repo import AIDemoRepository
from src.services.attendance_service import AIDemoService, get_ai_demo_runtime
from src.controller.attendance_controller import AttendanceController


def get_ai_demo_repo(db: AsyncSession = Depends(get_db)) -> AIDemoRepository:
    return AIDemoRepository(db)


def get_ai_demo_service(
    repo: AIDemoRepository = Depends(get_ai_demo_repo),
) -> AIDemoService:
    return AIDemoService(repo=repo, runtime=get_ai_demo_runtime())


def get_ai_demo_runtime_service() -> AIDemoService:
    return AIDemoService(repo=None, runtime=get_ai_demo_runtime())


def get_attendance_controller(
    service: AIDemoService = Depends(get_ai_demo_service),
) -> AttendanceController:
    return AttendanceController(service)
