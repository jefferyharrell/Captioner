from app.image_utils import LRUThumbnailCache


def test_lru_thumbnail_cache_full_coverage():
    cache = LRUThumbnailCache(max_bytes=10)
    # Add one item (4 bytes)
    cache.put("a", b"1234")
    assert cache.get("a") == b"1234"
    # Add a second item (6 bytes), total = 10 bytes, both fit
    cache.put("b", b"567890")
    assert cache.get("a") == b"1234"
    assert cache.get("b") == b"567890"
    # Add a third item (8 bytes), total would be 18, so eviction must occur
    cache.put("c", b"abcdefgh")
    # Only 'c' should remain (largest, most recent)
    assert cache.get("a") is None
    assert cache.get("b") is None
    assert cache.get("c") == b"abcdefgh"
    # Clear
    cache.clear()
    assert cache.get("c") is None
    assert cache.current_bytes == 0
