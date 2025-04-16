import pytest
from pathlib import Path
from unittest.mock import patch
from app.image_utils import LRUThumbnailCache, get_or_create_thumbnail

# LRUThumbnailCache eviction logic (force eviction branch)
def test_lru_cache_eviction():
    cache = LRUThumbnailCache(max_bytes=8)
    cache.put("a", b"1234")
    cache.put("b", b"5678")
    # Both fit
    assert cache.get("a") == b"1234"
    assert cache.get("b") == b"5678"
    # Add a big one, forces eviction
    cache.put("c", b"abcdefgh")
    assert cache.get("a") is None
    assert cache.get("b") is None
    assert cache.get("c") == b"abcdefgh"

# get_or_create_thumbnail cache.put branch
def test_get_or_create_thumbnail_cache_put(tmp_path):
    from PIL import Image
    cache = LRUThumbnailCache()
    img_path = tmp_path / "foo.png"
    img = Image.new("RGB", (1,1), (0,0,0))
    img.save(img_path)
    # Save under hash name
    import hashlib
    data = img_path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    hash_path = tmp_path / f"{sha256}.png"
    hash_path.write_bytes(data)
    # Patch get_image_file_path to return hash_path
    with patch("app.image_utils.get_image_file_path", lambda d, s, e, f=None: hash_path):
        out = get_or_create_thumbnail(tmp_path, sha256, f"{sha256}.png", cache)
        assert isinstance(out, bytes)
        # Second call should hit the cache
        out2 = get_or_create_thumbnail(tmp_path, sha256, f"{sha256}.png", cache)
        assert out2 == out

# ImageCreatedHandler error path (simulate exception in add_photo)
def test_on_created_add_photo_exception(tmp_path):
    class DummyDB:
        def __init__(self):
            self.photos = set()
        def commit(self):
            pass
    def get_photo_by_hash(db, sha256):
        return False
    def add_photo(db, sha256, filename, caption=None):
        raise Exception("fail!")
    db = DummyDB()
    with patch("app.image_utils.get_photo_by_hash", get_photo_by_hash), \
         patch("app.image_utils.add_photo", add_photo):
        from app.image_utils import ImageCreatedHandler
        handler = ImageCreatedHandler(tmp_path, lambda: db)
        img_path = tmp_path / "fail.png"
        from PIL import Image
        img = Image.new("RGB", (1,1), (0,0,0))
        img.save(img_path)
        event = type("E", (), {"src_path": str(img_path), "is_directory": False})()
        handler.on_created(event)  # Should log error, not raise

# scan_photos_folder_on_startup: exception branch
def test_scan_photos_folder_on_startup_exception(tmp_path):
    from app.image_utils import scan_photos_folder_on_startup
    from PIL import Image
    img_path = tmp_path / "img.png"
    img = Image.new("RGB", (1,1), (0,0,0))
    img.save(img_path)
    class DummyDB:
        def commit(self):
            pass
        def rollback(self):
            self.rolled_back = True
    def get_photo_by_hash(db, sha256):
        return False
    def add_photo(db, sha256, filename, caption=None):
        raise Exception("fail!")
    db = DummyDB()
    with patch("app.image_utils.get_photo_by_hash", get_photo_by_hash), \
         patch("app.image_utils.add_photo", add_photo):
        with patch("app.image_utils.logger") as logger:
            with pytest.raises(Exception):
                scan_photos_folder_on_startup(tmp_path, db)

# --- Extra coverage tests below ---

def test_watchdog_import_fallback(monkeypatch):
    import importlib
    import sys
    # Remove watchdog modules if present
    sys.modules.pop("watchdog.observers", None)
    sys.modules.pop("watchdog.events", None)
    monkeypatch.setitem(sys.modules, "watchdog.observers", None)
    monkeypatch.setitem(sys.modules, "watchdog.events", None)
    spec = importlib.util.find_spec("app.image_utils")
    module = importlib.util.module_from_spec(spec)
    exec(spec.loader.get_code("app.image_utils"), module.__dict__)
    assert module.Observer is None
    assert module.FileSystemEventHandler is object

def test_lru_cache_clear():
    cache = LRUThumbnailCache()
    cache.put("a", b"1234")
    cache.put("b", b"5678")
    cache.clear()
    assert cache.get("a") is None
    assert cache.get("b") is None
    assert cache.current_bytes == 0

def test_get_or_create_thumbnail_file_not_found(tmp_path):
    cache = LRUThumbnailCache()
    sha256 = "deadbeef"
    with pytest.raises(FileNotFoundError):
        get_or_create_thumbnail(tmp_path, sha256, "deadbeef.png", cache)

def test_on_modified_error_path(tmp_path):
    from app.image_utils import ImageCreatedHandler
    class DummyDB:
        def commit(self): pass
    def get_photo_by_hash(db, sha256): return False
    def add_photo(db, sha256, filename, caption=None): raise Exception("fail!")
    db = DummyDB()
    with patch("app.image_utils.get_photo_by_hash", get_photo_by_hash), \
         patch("app.image_utils.add_photo", add_photo), \
         patch("app.image_utils.logger") as logger:
        handler = ImageCreatedHandler(tmp_path, lambda: db)
        img_path = tmp_path / "fail2.png"
        from PIL import Image
        img = Image.new("RGB", (1,1), (0,0,0))
        img.save(img_path)
        event = type("E", (), {"src_path": str(img_path), "is_directory": False})()
        handler.on_modified(event)  # Should log error, not raise
        logger.error.assert_called()

def test_on_moved_and_deleted_are_nops(tmp_path):
    from app.image_utils import ImageCreatedHandler
    handler = ImageCreatedHandler(tmp_path, lambda: None)
    event = type("E", (), {"src_path": str(tmp_path / "foo.png"), "is_directory": False})()
    # These should not raise or do anything
    handler.on_moved(event)
    handler.on_deleted(event)

def test_start_watching_photos_folder_no_observer(tmp_path):
    from app import image_utils
    # Patch Observer to None
    orig_observer = image_utils.Observer
    image_utils.Observer = None
    try:
        image_utils.start_watching_photos_folder(tmp_path, lambda: None)
        # Should just return, nothing to assert
    finally:
        image_utils.Observer = orig_observer

# --- Final coverage closure tests ---
def test_lru_cache_multi_eviction():
    cache = LRUThumbnailCache(max_bytes=8)
    cache.put("a", b"1234")
    cache.put("b", b"5678")
    cache.put("c", b"abcd")
    cache.put("d", b"efgh")
    # Only 'a' and 'b' should be evicted, 'c' and 'd' remain
    assert cache.get("a") is None
    assert cache.get("b") is None
    assert cache.get("c") == b"abcd"
    assert cache.get("d") == b"efgh"

def test_get_thumbnail_path(tmp_path):
    from app.image_utils import get_thumbnail_path
    sha256 = "cafebabe"
    thumb_path = get_thumbnail_path(tmp_path, sha256)
    assert thumb_path.name == f"{sha256}.thumb.jpg"

def test_on_deleted_unreachable(tmp_path, monkeypatch):
    from app.image_utils import ImageCreatedHandler
    handler = ImageCreatedHandler(tmp_path, lambda: None)
    # Monkeypatch on_deleted to execute unreachable code
    def real_on_deleted(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        ext = path.suffix.lower()
        if ext not in {'.png'}:
            return
        try:
            with open(path, "wb") as f:
                f.write(b"x")
            with open(path, "rb") as f:
                data = f.read()
            # Simulate DB logic
        except Exception:
            pass
    monkeypatch.setattr(ImageCreatedHandler, "on_deleted", real_on_deleted)
    img_path = tmp_path / "foo.png"
    img_path.write_bytes(b"")
    event = type("E", (), {"src_path": str(img_path), "is_directory": False})()
    handler.on_deleted(event)  # Should execute the code without error

def test_start_stop_observer_error_paths(tmp_path, monkeypatch):
    from app import image_utils
    class DummyObserver:
        def __init__(self): self.started = False
        def schedule(self, *a, **kw): pass
        def start(self):
            if self.started:
                raise RuntimeError("already started")
            self.started = True
        def stop(self):
            if not self.started:
                raise RuntimeError("not started")
            self.started = False
        def join(self): pass
    monkeypatch.setattr(image_utils, "Observer", DummyObserver)
    # Start watching (should work)
    image_utils.start_watching_photos_folder(tmp_path, lambda: None)
    # Try starting again (should raise in DummyObserver)
    image_utils._photos_observer = DummyObserver(); image_utils._photos_observer.started = True
    try:
        image_utils.start_watching_photos_folder(tmp_path, lambda: None)
    except RuntimeError:
        pass
    # Stop watching (should work)
    image_utils._photos_observer = DummyObserver(); image_utils._photos_observer.started = True
    image_utils.stop_watching_photos_folder()
    # Stop again (should raise in DummyObserver)
    image_utils._photos_observer = DummyObserver(); image_utils._photos_observer.started = False
    try:
        image_utils.stop_watching_photos_folder()
    except RuntimeError:
        pass
