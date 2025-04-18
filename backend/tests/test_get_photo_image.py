import uuid
from fastapi.testclient import TestClient


def test_get_photo_image(test_app: TestClient) -> None:
    filename = f"imgfile_{uuid.uuid4().hex}.jpeg"
    fake_image = uuid.uuid4().bytes
    # Upload
    resp = test_app.post(
        "/photos", files={"file": (filename, fake_image, "image/jpeg")}
    )
    assert resp.status_code == 201
    data = resp.json()
    # GET image
    resp2 = test_app.get(f"/photos/{data['hash']}/image")
    assert resp2.status_code == 200
    assert resp2.headers["content-type"].startswith("image/")
    assert resp2.content == fake_image
    # GET with fake hash/filename
    resp3 = test_app.get("/photos/badhash/doesnotexist.jpg/image")
    assert resp3.status_code == 404
