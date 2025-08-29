from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.logger import logger
from app.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Vector Database API is running",
        "version": settings.app_version,
    }
