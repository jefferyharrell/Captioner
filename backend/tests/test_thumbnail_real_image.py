import io
import os
import pathlib
import pytest
from fastapi.testclient import TestClient
from app.main import create_app

pytestmark = pytest.mark.skipif(os.environ.get("CI") is not None, reason="Local-only test: image file not present in CI environment.")

@pytest.fixture
def client(tmp_path, monkeypatch):
    photos_dir = tmp_path / "photos"
    photos_dir.mkdir()
    db_path = tmp_path / "photos.db"
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models import Base
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    test_sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    app = create_app(photos_dir=photos_dir)
    app.state.db_sessionmaker = test_sessionmaker
    client = TestClient(app)
    monkeypatch.setenv("PASSWORD", "testpass")
    yield client

def test_thumbnail_generation_with_real_image(client):
    # Path to your real image file (adjust as needed)
    image_path = pathlib.Path(__file__).parent / "assets/ComfyUI_01209_.png"
    print(f"DEBUG: Looking for image at {image_path} (exists={image_path.exists()})")
    if not image_path.exists():
        pytest.fail(f"Real image not found at {image_path}")
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    resp = client.post("/photos", files={"file": ("ComfyUI_01209_.png", img_bytes, "image/png")})
    assert resp.status_code == 201
    photo = resp.json()
    hash = photo["hash"]
    resp2 = client.get(f"/photos/{hash}/thumbnail")
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}: {resp2.text}"
    thumb_bytes = resp2.content
    assert len(thumb_bytes) < len(img_bytes)
    # Should be a valid image
    from PIL import Image
    thumb = Image.open(io.BytesIO(thumb_bytes))
    assert thumb.width <= 256 and thumb.height <= 256
