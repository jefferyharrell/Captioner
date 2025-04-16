from pathlib import Path
import hashlib
import sqlite3
import uuid

def test_upload_duplicate_photo(test_app, temp_photos_dir):
    filename = f"dupe_{uuid.uuid4().hex}.jpeg"
    fake_image = b"dupeimg"
    test_hash = hashlib.sha256(fake_image).hexdigest()
    ext = Path(filename).suffix
    hashed_filename = f"{test_hash}{ext}"
    file_path = temp_photos_dir / hashed_filename
    # First upload
    resp1 = test_app.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp1.status_code == 201
    data1 = resp1.json()
    # Second upload (same content)
    resp2 = test_app.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp2.status_code == 409
    data2 = resp2.json()
    assert set(data2.keys()) == {"detail"}
    assert "hash already exists" in data2["detail"]
    assert isinstance(data2["detail"], str)
