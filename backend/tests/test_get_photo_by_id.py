import uuid
from pathlib import Path
from fastapi.testclient import TestClient


def test_get_photo_by_id(test_app: TestClient, temp_photos_dir: Path) -> None:
    filename = f"detail_{uuid.uuid4().hex}.jpeg"
    fake_image = uuid.uuid4().bytes
    # Upload
    resp = test_app.post(
        "/photos", files={"file": (filename, fake_image, "image/jpeg")}
    )
    assert resp.status_code == 201
    data = resp.json()
    # GET by hash
    resp2 = test_app.get(f"/photos/{data['hash']}")
    assert resp2.status_code == 200
    body = resp2.json()
    assert body["hash"] == data["hash"]
    assert body["filename"] == filename
    assert body["caption"] == data["caption"]
    # GET with fake hash/filename
    resp3 = test_app.get("/photos/badhash/doesnotexist.jpg")
    assert resp3.status_code == 404
