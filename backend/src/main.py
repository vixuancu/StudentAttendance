from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.config.settings import settings
from src.db.session import engine
from src.routes.router import api_router
from src.utils.exceptions import (
    AlreadyExistsException,
    BusinessException,
    NotFoundException,
    ValidationException,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print(f"✅ Starting {settings.app_name}...")
    yield
    await engine.dispose()
    print(f"❌ Shutting down {settings.app_name}...")


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# ===================== EXCEPTION HANDLERS ===================== #
# Chuyển BusinessException từ Service → HTTP Response tại đây,
# để Service layer KHÔNG cần biết gì về HTTP.


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


# ===================== ROUTES ===================== #
app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name} API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}