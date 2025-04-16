from pathlib import Path
import hashlib
import sqlite3

import uuid
import hashlib
from pathlib import Path
import sqlite3

def test_get_photo_by_id(test_app, temp_photos_dir):
    filename = f"detail_{uuid.uuid4().hex}.jpeg"
    fake_image = uuid.uuid4().bytes
    test_hash = hashlib.sha256(fake_image).hexdigest()
    # Clean up DB and image file before upload
    ext = Path(filename).suffix
    # Upload
    resp = test_app.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
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

    # Cleanup: remove the uploaded file if it exists (should be isolated by temp_photos_dir)
    file_path = temp_photos_dir / f"{data['hash']}{ext}"
    if file_path.exists():
        file_path.unlink()
