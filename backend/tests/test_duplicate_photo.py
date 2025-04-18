from pathlib import Path
import uuid
from fastapi.testclient import TestClient


def test_duplicate_photo(test_app: TestClient, temp_photos_dir: Path) -> None:
    filename = f"dupe_{uuid.uuid4().hex}.jpeg"
    fake_image = b"dupeimg"
    # First upload
    resp1 = test_app.post(
        "/photos", files={"file": (filename, fake_image, "image/jpeg")}
    )
    assert resp1.status_code == 201
    # Second upload (same content)
    resp2 = test_app.post(
        "/photos", files={"file": (filename, fake_image, "image/jpeg")}
    )
    assert resp2.status_code == 409
    data2 = resp2.json()
    assert set(data2.keys()) == {"detail"}
    assert "hash already exists" in data2["detail"]
    assert isinstance(data2["detail"], str)
