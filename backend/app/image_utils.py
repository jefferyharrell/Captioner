from pathlib import Path
import hashlib
from typing import Optional
from app.crud import get_photo_by_hash, add_photo
from app.models import Photo

import threading
import logging
logger = logging.getLogger(__name__)
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    Observer = None
    FileSystemEventHandler = object

# Allowed image extensions
ALLOWED_EXTS = {'.jpg', '.jpeg', '.png', '.heic', '.webp', '.tif', '.tiff'}

# Global observer for clean shutdown
_photos_observer = None

from collections import OrderedDict
from PIL import Image
import io
import threading
import os

class LRUThumbnailCache:
    def __init__(self, max_bytes=100*1024*1024):
        self.cache = OrderedDict()
        self.lock = threading.Lock()
        self.max_bytes = max_bytes
        self.current_bytes = 0

    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None
            value = self.cache.pop(key)
            self.cache[key] = value  # move to end
            return value

    def put(self, key, value):
        size = len(value)
        with self.lock:
            if key in self.cache:
                self.current_bytes -= len(self.cache[key])
                self.cache.pop(key)
            while self.current_bytes + size > self.max_bytes and self.cache:
                _, evicted = self.cache.popitem(last=False)
                self.current_bytes -= len(evicted)
            self.cache[key] = value
            self.current_bytes += size

    def clear(self):
        with self.lock:
            self.cache.clear()
            self.current_bytes = 0

def get_thumbnail_path(photos_dir: Path, sha256: str) -> Path:
    return photos_dir / f"{sha256}.thumb.jpg"

def generate_thumbnail(image_path: Path, max_size=256) -> bytes:
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img.thumbnail((max_size, max_size))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()

def get_or_create_thumbnail(photos_dir: Path, sha256: str, filename: str, cache: LRUThumbnailCache, max_size=256) -> bytes:
    ext = Path(filename).suffix
    img_path = get_image_file_path(photos_dir, sha256, ext)
    if not img_path.exists():
        raise FileNotFoundError("Image file not found.")
    cache_key = sha256
    thumb = cache.get(cache_key)
    if thumb is not None:
        return thumb
    thumb_bytes = generate_thumbnail(img_path, max_size=max_size)
    cache.put(cache_key, thumb_bytes)
    return thumb_bytes

class ImageCreatedHandler(FileSystemEventHandler):
    def __init__(self, photos_dir: Path, db_factory):
        super().__init__()
        self.photos_dir = photos_dir
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
            logger.info(f"Image created: {path} (sha256={sha256})")
        except Exception as e:
            logger.error(f"Exception while handling {path}: {e}")
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
            logger.info(f"Image created: {path} (sha256={sha256})")
        except Exception as e:
            logger.error(f"Exception while handling {path}: {e}")
    def on_moved(self, event):
        pass

    def on_deleted(self, event):
        pass

def start_watching_photos_folder(photos_dir: Path, db_factory):
    global _photos_observer

    if Observer is None:

        return  # watchdog not installed
    handler = ImageCreatedHandler(photos_dir, db_factory)
    observer = Observer()
    observer.schedule(handler, str(photos_dir), recursive=False)
    observer.daemon = True
    observer.start()

    _photos_observer = observer

def stop_watching_photos_folder():
    global _photos_observer
    if _photos_observer is not None:
        _photos_observer.stop()
        _photos_observer.join()
        _photos_observer = None

def hash_image_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def scan_photos_folder_on_startup(photos_dir: Path, db):  # db should come from injected sessionmaker in app.state for tests
    photos_dir.mkdir(parents=True, exist_ok=True)
    allowed_exts = {'.jpg', '.jpeg', '.png', '.heic', '.webp', '.tif', '.tiff'}
    for file in photos_dir.iterdir():
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
        import logging
        logger = logging.getLogger(__name__)
        try:
            add_photo(db, sha256, file.name, caption=None)
            db.commit()
            logger.info(f"Image created: {file} (sha256={sha256})")
        except Exception as e:
            # If this is an IntegrityError, it's a duplicate; otherwise, reraise
            from sqlalchemy.exc import IntegrityError
            if isinstance(e, IntegrityError):
                logger.info(f"Duplicate image skipped during scan: {file} (sha256={sha256})")
                db.rollback()
            else:
                logger.error(f"Error adding photo during scan: {file} (sha256={sha256}): {e}")
                raise

def save_image_file(photos_dir: Path, sha256: str, ext: str, data: bytes) -> Path:
    photos_dir.mkdir(parents=True, exist_ok=True)
    file_path = photos_dir / f"{sha256}{ext}"
    with file_path.open("wb") as buffer:
        buffer.write(data)
    return file_path

def get_image_file_path(photos_dir: Path, sha256: str, ext: str) -> Path:
    return photos_dir / f"{sha256}{ext}"
