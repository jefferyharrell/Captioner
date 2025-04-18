from pathlib import Path
from fastapi.testclient import TestClient


def test_rescan_endpoint_adds_new_image(
    test_app: TestClient, temp_photos_dir: Path
) -> None:
    # Place a new image in the folder
    import uuid

    img_path = temp_photos_dir / "test1.jpg"
    img_path.write_bytes(b"fakeimagedata1_" + uuid.uuid4().hex.encode())
    # Call rescan endpoint
    resp = test_app.post("/rescan")
    assert resp.status_code == 200
    assert resp.json() == {"detail": "Rescan started."}
    # Check that the image is now in /photos
    photos = test_app.get("/photos").json()
    assert any(p["filename"] == "test1.jpg" for p in photos)


def test_rescan_endpoint_idempotent(
    test_app: TestClient, temp_photos_dir: Path
) -> None:
    import uuid

    img_path = temp_photos_dir / "test2.png"
    img_path.write_bytes(b"fakeimagedata2_" + uuid.uuid4().hex.encode())
    # First rescan
    resp1 = test_app.post("/rescan")
    assert resp1.status_code == 200
    # Second rescan (should not duplicate)
    resp2 = test_app.post("/rescan")
    assert resp2.status_code == 200
    photos = test_app.get("/photos").json()
    filenames = [p["filename"] for p in photos]
    assert filenames.count("test2.png") == 1
