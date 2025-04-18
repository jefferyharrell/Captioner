import io
from pathlib import Path
import pytest
from typing import Generator, Tuple
from fastapi.testclient import TestClient
from PIL import Image
from app.main import create_app
from pytest import MonkeyPatch


@pytest.fixture
def client(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> Generator[TestClient, None, None]:
    # Set up a temporary photos dir and app
    photos_dir = tmp_path / "photos"
    photos_dir.mkdir()
    # Set up a unique SQLite DB per test
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import Base

    engine = create_engine(
        f"sqlite:///{tmp_path / 'photos.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    test_sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    app = create_app(photos_dir=photos_dir)
    app.state.db_sessionmaker = test_sessionmaker
    client = TestClient(app)
    # Patch the password for login
    monkeypatch.setenv("PASSWORD", "testpass")
    yield client


import random
from typing import Tuple


def make_image_bytes(
    size: Tuple[int, int] = (512, 512),
    color: Tuple[int, int, int] = (255, 0, 0),
    unique: int | None = None,
) -> bytes:
    img = Image.new("RGB", size, color)
    if unique is None:
        unique = random.randint(0, 2**24 - 1)
    x: int = unique % size[0]
    y: int = (unique // size[0]) % size[1]
    img.putpixel((x, y), (unique % 256, (unique >> 8) % 256, (unique >> 16) % 256))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_thumbnail_generation_and_serving(client: TestClient) -> None:
    # Upload an image
    img_bytes = make_image_bytes(unique=1)
    resp = client.post("/photos", files={"file": ("test.png", img_bytes, "image/png")})
    assert resp.status_code == 201
    photo = resp.json()
    hash = photo["hash"]
    # Request thumbnail
    resp2 = client.get(f"/photos/{hash}/thumbnail")
    assert resp2.status_code == 200
    assert resp2.headers["content-type"].startswith("image/")
    thumb_bytes = resp2.content
    # Should be smaller than original
    assert len(thumb_bytes) < len(img_bytes)
    # Should be a valid image
    thumb = Image.open(io.BytesIO(thumb_bytes))
    assert thumb.width <= 256 and thumb.height <= 256


def test_thumbnail_404_for_missing_photo(client: TestClient) -> None:
    resp = client.get("/photos/doesnotexist/thumbnail")
    assert resp.status_code == 404
    assert resp.json()["detail"]


def test_thumbnail_cache_eviction(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    # Set cache size to tiny for test
    monkeypatch.setenv("THUMBNAIL_CACHE_MB", "0.001")  # ~1KB
    photos_dir = tmp_path / "photos"
    photos_dir.mkdir()
    from app.main import create_app

    app = create_app(photos_dir=photos_dir)
    client = TestClient(app)

    import uuid

    img_bytes = make_image_bytes(
        size=(512, 512), color=(0, 255, 0), unique=uuid.uuid4().int
    )
    resp = client.post(
        "/photos",
        files={"file": (f"green_{uuid.uuid4().hex}.png", img_bytes, "image/png")},
    )
    resp_json = resp.json()
    if "hash" not in resp_json:
        print(f"DEBUG: Response JSON missing 'hash': {resp_json}")
    hash1 = resp_json["hash"]
    img_bytes2 = make_image_bytes(
        size=(512, 512), color=(0, 0, 255), unique=uuid.uuid4().int
    )
    resp2 = client.post(
        "/photos",
        files={"file": (f"blue_{uuid.uuid4().hex}.png", img_bytes2, "image/png")},
    )
    hash2 = resp2.json()["hash"]

    cache = app.state.thumbnail_cache
    # Request thumbnails for both
    client.get(f"/photos/{hash1}/thumbnail")
    assert hash1 in cache.cache
    client.get(f"/photos/{hash2}/thumbnail")
    assert hash2 in cache.cache
    # Now hash1 should be evicted (cache too small for both)
    assert hash1 not in cache.cache
    # Request hash1 again (should be regenerated and re-cached)
    client.get(f"/photos/{hash1}/thumbnail")
    assert hash1 in cache.cache
    assert hash2 not in cache.cache  # hash2 should now be evicted


def test_thumbnail_error_on_corrupt_image(client: TestClient, tmp_path: Path) -> None:
    # Upload a valid image to register in DB
    img_bytes = make_image_bytes(unique=99)
    resp = client.post(
        "/photos", files={"file": ("corrupt.png", img_bytes, "image/png")}
    )
    assert resp.status_code == 201
    photo = resp.json()
    hash = photo["hash"]
    # Overwrite the image file with corrupt data (use original filename, not hash)
    photos_dir = tmp_path / "photos"
    img_path = photos_dir / photo["filename"]
    img_path.write_bytes(b"not an image")
    # Now request thumbnail (should hit corrupt image path)
    resp = client.get(f"/photos/{hash}/thumbnail")
    assert resp.status_code == 500
    assert "detail" in resp.json()
