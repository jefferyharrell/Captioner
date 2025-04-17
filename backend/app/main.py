import sys
import logging
from app.logging_config import setup_logging

# Initialize logging before anything else
setup_logging()

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from starlette.responses import Response

from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

def create_app(photos_dir=None):
    from app.routes.photos import router as photos_router
    from app.routes.auth import router as auth_router
    from app.db import get_db
    from app.image_utils import scan_photos_folder_on_startup, LRUThumbnailCache
    from pathlib import Path
    import os

    def db_factory():
        db_gen = get_db(session_maker=app.state.db_sessionmaker if hasattr(app.state, "db_sessionmaker") else None)
        db = next(db_gen)
        return db

    # Initialize thumbnail cache
    max_mb = float(os.environ.get("THUMBNAIL_CACHE_MB", "100"))
    thumbnail_cache = LRUThumbnailCache(int(max_mb * 1024 * 1024))

    # Attach cache to app.state
    # (app is not yet defined, so we'll do this after app creation below)


    @asynccontextmanager
    async def lifespan(app):
        db_gen = get_db(session_maker=app.state.db_sessionmaker if hasattr(app.state, "db_sessionmaker") else None)
        db = next(db_gen)
        try:
            scan_photos_folder_on_startup(app.state.photos_dir, db)
            yield
        finally:
            db_gen.close()

    logger = logging.getLogger("app.main")
    app = FastAPI(lifespan=lifespan)
    app.state.thumbnail_cache = thumbnail_cache
    logger.info("FastAPI app instantiated.")

    # Set the photos_dir on app.state (for both prod and test)
    if photos_dir is None:
        app.state.photos_dir = Path(__file__).parent.parent / "photos"
    else:
        app.state.photos_dir = photos_dir
    logger.info(f"Photos directory set to: {app.state.photos_dir}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    @app.get("/")
    def read_root():
        return {"message": "Hello, world!"}

    app.include_router(photos_router)
    app.include_router(auth_router)

    return app

app = create_app()
