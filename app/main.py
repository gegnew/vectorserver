from contextlib import asynccontextmanager

from fastapi import FastAPI

from .logger import logger
from .routes import libraries_router, search_router
from .settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Vector Database API startup complete")
    yield
    logger.info("Vector Database API shutdown")


app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)
app.include_router(libraries_router)
app.include_router(search_router)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Vector Database API is running",
        "version": settings.app_version,
    }


@app.get("/health")
async def health_check():
    logger.info("Health check accessed")
    return {
        "status": "healthy",
        "service": settings.app_title,
        "version": settings.app_version,
    }
