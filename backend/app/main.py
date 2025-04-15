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
    # Check for duplicate hash
    existing = db.query(Photo).filter_by(hash=sha256).first()
    if existing:
        db.close()
        raise HTTPException(status_code=409, detail="Photo with this content already exists.")
    file_path = images_dir / hashed_filename
    with file_path.open("wb") as buffer:
        buffer.write(contents)
    photo_id = str(uuid.uuid4())
    photo = Photo(id=photo_id, filename=file.filename, hash=sha256, caption=None)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    db.close()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "id": photo.id,
            "filename": photo.filename,
            "hash": photo.hash,
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
            "id": p.id,
            "filename": p.filename,
            "hash": p.hash,
            "caption": p.caption
        }
        for p in photos
    ]

@app.get("/photos/{photo_id}")
def get_photo_by_id(photo_id: str):
    db = SessionLocal()
    photo = db.query(Photo).filter_by(id=photo_id).first()
    db.close()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    return {
        "id": photo.id,
        "filename": photo.filename,
        "hash": photo.hash,
        "caption": photo.caption
    }

from fastapi import Body
from fastapi.responses import FileResponse
import mimetypes

@app.patch("/photos/{photo_id}/caption")
def patch_photo_caption(photo_id: str, caption: str = Body(..., embed=True)):
    db = SessionLocal()
    photo = db.query(Photo).filter_by(id=photo_id).first()
    if not photo:
        db.close()
        raise HTTPException(status_code=404, detail="Photo not found.")
    photo.caption = caption
    db.commit()
    db.refresh(photo)
    db.close()
    return {
        "id": photo.id,
        "filename": photo.filename,
        "hash": photo.hash,
        "caption": photo.caption
    }

@app.get("/photos/{photo_id}/image")
def get_photo_image(photo_id: str):
    db = SessionLocal()
    photo = db.query(Photo).filter_by(id=photo_id).first()
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
