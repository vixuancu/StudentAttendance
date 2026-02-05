from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.config.settings import settings
from src.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print(f"✅ Starting {settings.app_name}...")
    yield
    # Shutdown
    await engine.dispose()
    print(f"❌ Shutting down {settings.app_name}...")


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name} API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}