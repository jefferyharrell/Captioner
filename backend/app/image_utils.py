from pathlib import Path
import hashlib
from typing import Optional

def hash_image_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def save_image_file(images_dir: Path, sha256: str, ext: str, data: bytes) -> Path:
    images_dir.mkdir(parents=True, exist_ok=True)
    file_path = images_dir / f"{sha256}{ext}"
    with file_path.open("wb") as buffer:
        buffer.write(data)
    return file_path

def get_image_file_path(images_dir: Path, sha256: str, ext: str) -> Path:
    return images_dir / f"{sha256}{ext}"
