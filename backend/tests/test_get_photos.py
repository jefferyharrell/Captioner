from pathlib import Path
import hashlib
import sqlite3

def test_get_photos(test_app, temp_photos_dir):
    # Upload two photos with different content
    files = [
        ("photo1.jpeg", b"img1_unique_content"),
        ("photo2.jpeg", b"img2_different_content")
    ]
    uploaded = []
    for fname, data in files:
        resp = test_app.post("/photos", files={"file": (fname, data, "image/jpeg")})
        assert resp.status_code == 201
        uploaded.append(resp.json())
    # GET /photos
    resp = test_app.get("/photos")
    assert resp.status_code == 200
    photos = resp.json()
    # Both uploaded photos should be present
    for up in uploaded:
        match = next((p for p in photos if p["hash"] == up["hash"] and p["filename"] == up["filename"]), None)
        assert match is not None
        assert match["caption"] == up["caption"]
