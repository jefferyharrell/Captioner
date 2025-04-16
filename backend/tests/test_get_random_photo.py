from pathlib import Path
import pytest

def test_get_random_photo_multiple(test_app, temp_photos_dir):
    # Upload three photos with unique content
    files = [
        ("photo1.jpg", b"img1_unique_content"),
        ("photo2.jpg", b"img2_unique_content"),
        ("photo3.jpg", b"img3_unique_content"),
    ]
    uploaded = []
    for fname, data in files:
        resp = test_app.post("/photos", files={"file": (fname, data, "image/jpeg")})
        assert resp.status_code == 201
        uploaded.append(resp.json())
    # Diagnostic: print /photos result
    resp = test_app.get("/photos")
    print("/photos result after upload:", resp.json())
    # Call /photos/random multiple times; collect returned hashes
    seen_hashes = set()
    for _ in range(15):
        resp = test_app.get("/photos/random")
        assert resp.status_code == 200
        photo = resp.json()
        seen_hashes.add(photo["hash"])
        # Valid response fields
        assert "filename" in photo
        assert "caption" in photo
    # All uploaded photos should be seen at least once
    uploaded_hashes = {p["hash"] for p in uploaded}
    assert seen_hashes == uploaded_hashes

def test_get_random_photo_single(test_app, temp_photos_dir):
    resp = test_app.post("/photos", files={"file": ("only.jpg", b"unique_data", "image/jpeg")})
    assert resp.status_code == 201
    up = resp.json()
    # Should always return the only photo
    for _ in range(5):
        resp = test_app.get("/photos/random")
        assert resp.status_code == 200
        photo = resp.json()
        assert photo["hash"] == up["hash"]
        assert photo["filename"] == up["filename"]

def test_get_random_photo_empty_db(test_app):
    resp = test_app.get("/photos/random")
    assert resp.status_code == 404
    detail = resp.json()["detail"]
    assert "No photos" in detail or "not found" in detail.lower()
