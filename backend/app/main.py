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
