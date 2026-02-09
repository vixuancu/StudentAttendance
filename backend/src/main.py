"""
FastAPI Application Entry Point.
  - Lifespan: startup / graceful shutdown
  - Exception handlers: BusinessException → HTTP
  - Global error handlers: 404 route, 500 unhandled
  - Middleware: CORS, RequestLogging
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config.logging_config import setup_logging
from src.config.settings import settings
from src.db.session import engine
from src.middleware.cors import setup_cors
from src.middleware.logging_middleware import RequestLoggingMiddleware
from src.routes.router import api_router
from src.utils.exceptions import (
    AlreadyExistsException,
    BusinessException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)

# Khởi tạo logging trước khi tạo app
setup_logging()
logger = logging.getLogger(__name__)


# ===================== LIFESPAN (startup + graceful shutdown) ============ #
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup và Graceful Shutdown."""
    logger.info("✅ Starting %s (env=%s)...", settings.app_name, settings.app_env)
    logger.info(
        "🔗 DB pool: size=%d, max_overflow=%d, recycle=%ds",
        settings.db_pool_size,
        settings.db_max_overflow,
        settings.db_pool_recycle,
    )
    yield
    # ── Graceful Shutdown ──
    logger.info("⏳ Đang đóng connection pool...")
    await engine.dispose()
    logger.info("❌ %s đã shutdown.", settings.app_name)


# ===================== CREATE APP ======================================== #
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# ===================== MIDDLEWARE ======================================== #
# Thứ tự add middleware: sau cùng add = chạy ĐẦU TIÊN
setup_cors(app)
app.add_middleware(RequestLoggingMiddleware)


# ===================== BUSINESS EXCEPTION HANDLERS ====================== #
# Service throw BusinessException → convert thành HTTP response tại đây.


@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(_request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=401,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(ForbiddenException)
async def forbidden_handler(_request: Request, exc: ForbiddenException):
    return JSONResponse(
        status_code=403,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
        },
    )


@app.exception_handler(NotFoundException)
async def not_found_handler(_request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
        },
    )


@app.exception_handler(AlreadyExistsException)
async def already_exists_handler(_request: Request, exc: AlreadyExistsException):
    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
        },
    )


@app.exception_handler(ValidationException)
async def validation_handler(_request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
        },
    )


@app.exception_handler(BusinessException)
async def business_handler(_request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
        },
    )


# ===================== GLOBAL HTTP EXCEPTION HANDLERS =================== #
# Xử lý lỗi HTTP chung (404 route không tồn tại, 405 method not allowed, ...)
# → Trả JSON thống nhất thay vì {"detail": "Not Found"} mặc định.


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Bắt tất cả HTTPException (404, 405, 500, ...) → trả JSON format thống nhất.
    Đặc biệt khi gọi URL không tồn tại → thay vì "Not Found" khó hiểu,
    sẽ trả thông tin rõ ràng kèm method + path.
    """
    # Map status code → thông điệp dễ hiểu
    error_messages = {
        404: f"Không tìm thấy route: {request.method} {request.url.path}",
        405: f"Method {request.method} không được hỗ trợ cho {request.url.path}",
        500: "Lỗi máy chủ nội bộ. Vui lòng thử lại sau.",
    }

    message = error_messages.get(exc.status_code, str(exc.detail))

    logger.warning(
        "HTTP %d: %s %s → %s",
        exc.status_code,
        request.method,
        request.url.path,
        message,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": message,
            "error_code": f"HTTP_{exc.status_code}",
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(
    request: Request, exc: RequestValidationError
):
    """
    Pydantic validation error → trả JSON rõ ràng thay vì mảng lỗi phức tạp.
    """
    errors = exc.errors()
    # Tạo danh sách lỗi dễ đọc
    details = []
    for err in errors:
        field = " → ".join(str(loc) for loc in err["loc"])
        details.append({"field": field, "message": err["msg"], "type": err["type"]})

    logger.warning("Validation error: %s %s → %s", request.method, request.url.path, details)

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Dữ liệu đầu vào không hợp lệ",
            "error_code": "VALIDATION_ERROR",
            "details": details,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Bắt mọi exception không xử lý được → log + trả 500.
    Tránh lộ stack trace cho client.
    """
    logger.exception(
        "Unhandled exception: %s %s → %s: %s",
        request.method,
        request.url.path,
        type(exc).__name__,
        str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Lỗi máy chủ nội bộ. Vui lòng thử lại sau.",
            "error_code": "INTERNAL_ERROR",
        },
    )


# ===================== ROUTES =========================================== #
app.include_router(api_router)


@app.get("/", tags=["Health"])
async def root():
    return {"message": f"Welcome to {settings.app_name} API"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "env": settings.app_env}