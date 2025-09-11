import uvicorn

from app.settings import settings


def main():
    """Run the FastAPI application."""
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        reload_excludes=[".venv"],
        reload_dirs=["app/"],
    )


if __name__ == "__main__":
    main()
