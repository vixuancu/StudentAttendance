"""
Main Router – include tất cả route modules v1.
"""

from fastapi import APIRouter

from src.routes.v1 import (
    account_routes,
    student_routes,
    camera_routes,
    classrooms_routes,
    administrative_class_routes,
    course_routes,
    course_section_routes,
    auth_routes,
)

# from src.routes.v1 import user_routes
# from src.routes.v1 import course_routes
# from src.routes.v1 import attendance_routes

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_routes.router)
api_router.include_router(student_routes.router)
api_router.include_router(administrative_class_routes.router)
api_router.include_router(account_routes.router)
api_router.include_router(camera_routes.router)
api_router.include_router(classrooms_routes.router)
api_router.include_router(course_routes.router)
api_router.include_router(course_section_routes.router)
# api_router.include_router(user_routes.router)
# api_router.include_router(course_routes.router)
# api_router.include_router(attendance_routes.router)
