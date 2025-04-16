from pathlib import Path
import hashlib
from typing import Optional
from app.crud import get_photo_by_hash, add_photo
from app.models import Photo

def hash_image_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scan_images_folder_on_startup(images_dir: Path, db):
    """
    Scan images_dir for files, hash each, and add to DB if not present.
    """
    images_dir.mkdir(parents=True, exist_ok=True)
    allowed_exts = {'.jpg', '.jpeg', '.png', '.heic', '.webp', '.tif', '.tiff'}
    for file in images_dir.iterdir():
        if not file.is_file():
            continue
        ext = file.suffix.lower()
        if ext not in allowed_exts:
            continue
        with open(file, "rb") as f:
            data = f.read()
        sha256 = hashlib.sha256(data).hexdigest()
        if get_photo_by_hash(db, sha256):
            continue
        add_photo(db, sha256, file.name, caption=None)

def save_image_file(images_dir: Path, sha256: str, ext: str, data: bytes) -> Path:
    images_dir.mkdir(parents=True, exist_ok=True)
    file_path = images_dir / f"{sha256}{ext}"
    with file_path.open("wb") as buffer:
        buffer.write(data)
    return file_path

def get_image_file_path(images_dir: Path, sha256: str, ext: str) -> Path:
    return images_dir / f"{sha256}{ext}"
