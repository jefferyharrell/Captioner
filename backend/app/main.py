from fastapi import FastAPI, UploadFile, File, status
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path
import uuid
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Photo

app = FastAPI()

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from starlette.responses import Response

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

from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi import Request
from pydantic import BaseModel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class LoginRequest(BaseModel):
    password: str

@app.post("/login")
def login(data: LoginRequest):
    password = os.environ.get("PASSWORD", "letmein")
    if data.password == password:
        return {"success": True}
    return {"success": False}

# Set up DB (SQLite, using pathlib)
db_path = Path(__file__).parent.parent / "photos.db"
engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

from fastapi import HTTPException

@app.post("/photos", status_code=201)
def upload_photo(file: UploadFile = File(...)):
    images_dir = Path(__file__).parent.parent / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    contents = file.file.read()
    sha256 = hashlib.sha256(contents).hexdigest()
    ext = Path(file.filename).suffix
    hashed_filename = f"{sha256}{ext}"
    db = SessionLocal()
    # Check for duplicate (hash, filename)
    existing = db.query(Photo).filter_by(hash=sha256, filename=file.filename).first()
    if existing:
        db.close()
        raise HTTPException(status_code=409, detail="Photo with this hash and filename already exists.")
    file_path = images_dir / hashed_filename
    with file_path.open("wb") as buffer:
        buffer.write(contents)
    photo = Photo(hash=sha256, filename=file.filename, caption=None)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    db.close()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "hash": photo.hash,
            "filename": photo.filename,
            "caption": photo.caption
        }
    )

@app.get("/photos")
def get_photos():
    db = SessionLocal()
    photos = db.query(Photo).all()
    db.close()
    return [
        {
            "hash": p.hash,
            "filename": p.filename,
            "caption": p.caption
        }
        for p in photos
    ]

@app.get("/photos/{hash}/{filename}")
def get_photo_by_hash_filename(hash: str, filename: str):
    db = SessionLocal()
    photo = db.query(Photo).filter_by(hash=hash, filename=filename).first()
    db.close()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    return {
        "hash": photo.hash,
        "filename": photo.filename,
        "caption": photo.caption
    }

from fastapi import Body
from fastapi.responses import FileResponse
import mimetypes

@app.patch("/photos/{hash}/{filename}/caption")
def patch_photo_caption(hash: str, filename: str, caption: str = Body(..., embed=True)):
    db = SessionLocal()
    photo = db.query(Photo).filter_by(hash=hash, filename=filename).first()
    if not photo:
        db.close()
        raise HTTPException(status_code=404, detail="Photo not found.")
    photo.caption = caption
    db.commit()
    db.refresh(photo)
    db.close()
    return {
        "hash": photo.hash,
        "filename": photo.filename,
        "caption": photo.caption
    }

@app.get("/photos/{hash}/{filename}/image")
def get_photo_image(hash: str, filename: str):
    db = SessionLocal()
    photo = db.query(Photo).filter_by(hash=hash, filename=filename).first()
    db.close()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    ext = Path(photo.filename).suffix
    images_dir = Path(__file__).parent.parent / "images"
    file_path = images_dir / f"{photo.hash}{ext}"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found.")
    mimetype, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(path=file_path, media_type=mimetype or "application/octet-stream")
