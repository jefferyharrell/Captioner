from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from starlette.responses import Response

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

app.include_router(photos_router)
app.include_router(auth_router)
