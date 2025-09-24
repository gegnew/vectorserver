from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .logger import logger
from .models.responses import HealthCheck
from .repositories.db import create_db
from .routes import chunks_router, indexes_router, libraries_router, search_router
from .routes.documents import router as documents_router
from .settings import settings

# Fix forward references after all imports
from .models.models import SearchResult
from .models.document import Document

SearchResult.model_rebuild()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifespan for database connections."""
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
app.include_router(chunks_router)
app.include_router(indexes_router)
app.include_router(libraries_router)
app.include_router(search_router)
app.include_router(documents_router)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root requests to API documentation."""
    logger.info("Root endpoint accessed")
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Return API and database health status."""
    logger.info("Health check accessed")

    try:
        # Simple database check - could be enhanced with actual health query
        db_status = "healthy" if app.state.db else "unhealthy"
    except Exception:
        db_status = "unhealthy"

    return HealthCheck(
        status="healthy" if db_status == "healthy" else "degraded",
        version=settings.app_version,
        services={"database": db_status, "api": "healthy"},
    )
