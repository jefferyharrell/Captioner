from pathlib import Path
import hashlib
from typing import Optional
from app.crud import get_photo_by_hash, add_photo
from app.models import Photo

import threading
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    Observer = None
    FileSystemEventHandler = object

# Allowed image extensions
ALLOWED_EXTS = {'.jpg', '.jpeg', '.png', '.heic', '.webp', '.tif', '.tiff'}

# Global observer for clean shutdown
_images_observer = None

class ImageCreatedHandler(FileSystemEventHandler):
    def __init__(self, images_dir: Path, db_factory):
        super().__init__()
        self.images_dir = images_dir
        self.db_factory = db_factory  # Callable that returns a new DB session/connection

    def on_created(self, event):

        if event.is_directory:

            return
        path = Path(event.src_path)
        ext = path.suffix.lower()
        if ext not in ALLOWED_EXTS:

            return
        try:
            with open(path, "rb") as f:
                data = f.read()
            sha256 = hashlib.sha256(data).hexdigest()
            db = self.db_factory()
            if not get_photo_by_hash(db, sha256):
                add_photo(db, sha256, path.name, caption=None)
        except Exception as e:
            print(f"Exception while handling {path}: {e}")
    def on_modified(self, event):

        if event.is_directory:

            return
        path = Path(event.src_path)
        ext = path.suffix.lower()
        if ext not in ALLOWED_EXTS:

            return
        try:
            with open(path, "rb") as f:
                data = f.read()
            sha256 = hashlib.sha256(data).hexdigest()
            db = self.db_factory()
            if not get_photo_by_hash(db, sha256):
                add_photo(db, sha256, path.name, caption=None)
        except Exception as e:
            print(f"Exception while handling {path}: {e}")
    def on_moved(self, event):
        pass

    def on_deleted(self, event):
        pass

        if event.is_directory:

            return
        path = Path(event.src_path)
        ext = path.suffix.lower()
        if ext not in ALLOWED_EXTS:

            return
        try:
            with open(path, "rb") as f:
                data = f.read()
            sha256 = hashlib.sha256(data).hexdigest()
            db = self.db_factory()
            if not get_photo_by_hash(db, sha256):
                add_photo(db, sha256, path.name, caption=None)
        except Exception as e:
            print(f"Exception while handling {path}: {e}")

def start_watching_images_folder(images_dir: Path, db_factory):
    global _images_observer

    if Observer is None:

        return  # watchdog not installed
    handler = ImageCreatedHandler(images_dir, db_factory)
    observer = Observer()
    observer.schedule(handler, str(images_dir), recursive=False)
    observer.daemon = True
    observer.start()

    _images_observer = observer

def stop_watching_images_folder():
    global _images_observer
    if _images_observer is not None:
        _images_observer.stop()
        _images_observer.join()
        _images_observer = None

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
