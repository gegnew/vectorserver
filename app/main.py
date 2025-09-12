from contextlib import asynccontextmanager

from fastapi import FastAPI

from .logger import logger
from .repositories.db import create_db
from .routes import libraries_router, search_router
from .routes.documents import router as documents_router
from .settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database connection...")
    app.state.db = await create_db()
    logger.info("Vector Database API startup complete")
    yield
    logger.info("Closing database connection...")
    await app.state.db.close()
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
app.include_router(documents_router)


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
