from fastapi import APIRouter, UploadFile, File, HTTPException, status, Body, Depends
from fastapi.responses import JSONResponse, FileResponse
from app.schemas import PhotoResponse
from app.crud import add_photo, get_photo_by_hash_filename, get_all_photos, update_photo_caption
from app.db import get_db
from app.models import Photo
from app.image_utils import hash_image_bytes, save_image_file, get_image_file_path
from sqlalchemy.orm import Session
from pathlib import Path
import mimetypes

router = APIRouter()

IMAGES_DIR = Path(__file__).parent.parent.parent / "images"

@router.post("/photos", response_model=PhotoResponse, status_code=201)
def upload_photo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = file.file.read()
    sha256 = hash_image_bytes(contents)
    ext = Path(file.filename).suffix
    existing = get_photo_by_hash_filename(db, sha256, file.filename)
    if existing:
        raise HTTPException(status_code=409, detail="Photo with this hash and filename already exists.")
    save_image_file(IMAGES_DIR, sha256, ext, contents)
    photo = add_photo(db, sha256, file.filename, caption=None)
    return PhotoResponse(hash=photo.hash, filename=photo.filename, caption=photo.caption)

@router.get("/photos", response_model=list[PhotoResponse])
def get_photos(db: Session = Depends(get_db)):
    return [PhotoResponse(hash=p.hash, filename=p.filename, caption=p.caption) for p in get_all_photos(db)]

@router.get("/photos/{hash}/{filename}", response_model=PhotoResponse)
def get_photo_by_hash_filename_route(hash: str, filename: str, db: Session = Depends(get_db)):
    photo = get_photo_by_hash_filename(db, hash, filename)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    return PhotoResponse(hash=photo.hash, filename=photo.filename, caption=photo.caption)

@router.patch("/photos/{hash}/{filename}/caption", response_model=PhotoResponse)
def patch_photo_caption_route(hash: str, filename: str, caption: str = Body(..., embed=True), db: Session = Depends(get_db)):
    photo = update_photo_caption(db, hash, filename, caption)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    return PhotoResponse(hash=photo.hash, filename=photo.filename, caption=photo.caption)

@router.get("/photos/{hash}/{filename}/image")
def get_photo_image(hash: str, filename: str, db: Session = Depends(get_db)):
    photo = get_photo_by_hash_filename(db, hash, filename)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    ext = Path(photo.filename).suffix
    file_path = get_image_file_path(IMAGES_DIR, photo.hash, ext)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found.")
    mimetype, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(path=file_path, media_type=mimetype or "application/octet-stream")
