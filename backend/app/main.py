import sys

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from starlette.responses import Response

from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

def create_app():

    from app.routes.photos import router as photos_router
    from app.routes.auth import router as auth_router
    from app.db import get_db
    from app.image_utils import scan_images_folder_on_startup, start_watching_images_folder, stop_watching_images_folder
    from pathlib import Path

    IMAGES_DIR = Path(__file__).parent.parent / "images"

    def db_factory():
        # Returns a new DB connection/session for watchdog handler
        db_gen = get_db()
        db = next(db_gen)
        return db

    @asynccontextmanager
    async def lifespan(app):

        db_gen = get_db()
        db = next(db_gen)
        try:

            scan_images_folder_on_startup(IMAGES_DIR, db)
    
            start_watching_images_folder(IMAGES_DIR, db_factory)
    
            yield
        finally:
    
            stop_watching_images_folder()
            db_gen.close()

    app = FastAPI(lifespan=lifespan)

    @app.exception_handler(FastAPIHTTPException)
    async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
        code_map = {404: "NotFound", 409: "Conflict"}
        error_type = code_map.get(exc.status_code, exc.status_code)
        message = exc.detail if exc.detail else str(exc.status_code)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": error_type, "message": message}
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "InternalServerError", "message": str(exc)}
        )

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

@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    code_map = {404: "NotFound", 409: "Conflict"}
    error_type = code_map.get(exc.status_code, exc.status_code)
    # Use exc.detail as message, fallback to status phrase
    message = exc.detail if exc.detail else str(exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": error_type, "message": message}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "message": str(exc)}
    )

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

# Routers
from app.routes.photos import router as photos_router
from app.routes.auth import router as auth_router
from app.db import get_db
from app.image_utils import scan_images_folder_on_startup
from pathlib import Path

IMAGES_DIR = Path(__file__).parent.parent / "images"


app.include_router(photos_router)
app.include_router(auth_router)
