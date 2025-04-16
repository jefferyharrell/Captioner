import io
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.image_utils import ImageCreatedHandler, ALLOWED_EXTS

class DummyEvent:
    def __init__(self, src_path, is_directory=False):
        self.src_path = src_path
        self.is_directory = is_directory

def make_image_bytes():
    try:
        from PIL import Image
    except ImportError:
        pytest.skip("PIL not available")
    img = Image.new("RGB", (10, 10), (123, 222, 111))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def test_on_created_directory_event(tmp_path):
    handler = ImageCreatedHandler(tmp_path, lambda: None)
    event = DummyEvent(str(tmp_path / "subdir"), is_directory=True)
    handler.on_created(event)  # Should do nothing, just cover the branch

def test_on_created_non_image_file(tmp_path):
    handler = ImageCreatedHandler(tmp_path, lambda: None)
    file_path = tmp_path / "notanimage.txt"
    file_path.write_text("not an image")
    event = DummyEvent(str(file_path))
    handler.on_created(event)  # Should do nothing (not in ALLOWED_EXTS)

def test_on_created_valid_image(tmp_path):
    # Minimal DB mock
    class DummyDB:
        def __init__(self):
            self.photos = set()
        def commit(self):
            pass
    def get_photo_by_hash(db, sha256):
        return sha256 in db.photos
    def add_photo(db, sha256, filename, caption=None):
        db.photos.add(sha256)
    db = DummyDB()
    # Patch app.crud for isolation
    with patch("app.image_utils.get_photo_by_hash", get_photo_by_hash), \
         patch("app.image_utils.add_photo", add_photo):
        handler = ImageCreatedHandler(tmp_path, lambda: db)
        img_path = tmp_path / "foo.png"
        img_path.write_bytes(make_image_bytes())
        event = DummyEvent(str(img_path))
        handler.on_created(event)
        # Should now have one photo
        assert len(db.photos) == 1

def test_on_created_duplicate_image(tmp_path):
    class DummyDB:
        def __init__(self):
            self.photos = set()
        def commit(self):
            pass
    def get_photo_by_hash(db, sha256):
        return True  # Always a duplicate
    def add_photo(db, sha256, filename, caption=None):
        raise AssertionError("Should not be called for duplicate")
    db = DummyDB()
    with patch("app.image_utils.get_photo_by_hash", get_photo_by_hash), \
         patch("app.image_utils.add_photo", add_photo):
        handler = ImageCreatedHandler(tmp_path, lambda: db)
        img_path = tmp_path / "bar.png"
        img_path.write_bytes(make_image_bytes())
        event = DummyEvent(str(img_path))
        handler.on_created(event)  # Should not call add_photo

def test_on_created_exception(tmp_path):
    # Simulate file open/read error
    handler = ImageCreatedHandler(tmp_path, lambda: None)
    file_path = tmp_path / "bad.png"
    file_path.write_bytes(b"not an image")
    event = DummyEvent(str(file_path))
    with patch("builtins.open", side_effect=OSError("kaboom")):
        handler.on_created(event)  # Should log error, not raise

def test_on_modified_branches(tmp_path):
    # Just call on_modified for directory, non-image, and valid image
    handler = ImageCreatedHandler(tmp_path, lambda: None)
    # Directory event
    event_dir = DummyEvent(str(tmp_path / "dir"), is_directory=True)
    handler.on_modified(event_dir)
    # Non-image file
    file_path = tmp_path / "baz.txt"
    file_path.write_text("not an image")
    event_nonimg = DummyEvent(str(file_path))
    handler.on_modified(event_nonimg)
    # Valid image
    class DummyDB:
        def __init__(self):
            self.photos = set()
        def commit(self):
            pass
    def get_photo_by_hash(db, sha256):
        return sha256 in db.photos
    def add_photo(db, sha256, filename, caption=None):
        db.photos.add(sha256)
    db = DummyDB()
    with patch("app.image_utils.get_photo_by_hash", get_photo_by_hash), \
         patch("app.image_utils.add_photo", add_photo):
        img_path = tmp_path / "baz.png"
        img_path.write_bytes(make_image_bytes())
        event_img = DummyEvent(str(img_path))
        handler2 = ImageCreatedHandler(tmp_path, lambda: db)
        handler2.on_modified(event_img)
        assert len(db.photos) == 1

def test_on_moved_and_deleted_are_noops(tmp_path):
    handler = ImageCreatedHandler(tmp_path, lambda: None)
    event = DummyEvent(str(tmp_path / "foo.png"))
    # These should not raise or do anything
    handler.on_moved(event)
    handler.on_deleted(event)

def test_start_watching_photos_folder_no_watchdog(tmp_path):
    # Patch Observer to None to simulate watchdog not installed
    with patch("app.image_utils.Observer", None):
        from app.image_utils import start_watching_photos_folder
        # Should do nothing (no error)
        start_watching_photos_folder(tmp_path, lambda: None)
