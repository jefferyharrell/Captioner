import pytest
from pathlib import Path
from app.image_utils import LRUThumbnailCache, generate_thumbnail, get_image_file_path


def test_lru_thumbnail_cache_put_overwrite(tmp_path: Path):
    cache = LRUThumbnailCache(max_bytes=100)
    cache.put("foo", b"abc")
    cache.put("foo", b"defg")  # Overwrite, should update value and current_bytes
    assert cache.get("foo") == b"defg"
    assert cache.current_bytes == len(b"defg")


def test_generate_thumbnail_permission_error(tmp_path: Path):
    # Create a file and remove read permission to trigger OSError
    img_path = tmp_path / "no_access.png"
    img_path.write_bytes(b"not an image")
    img_path.chmod(0o000)
    try:
        with pytest.raises(Exception):
            generate_thumbnail(img_path)
    finally:
        img_path.chmod(0o644)  # Restore so tmp_path can clean up


def test_get_image_file_path_hash_fallback(tmp_path: Path):
    # Should use hash+ext fallback if original_filename is None
    photos_dir = tmp_path
    sha256 = "deadbeef"
    ext = ".jpg"
    path = get_image_file_path(photos_dir, sha256, ext, original_filename=None)
    assert path == photos_dir / f"{sha256}{ext}"
