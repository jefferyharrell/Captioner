from pathlib import Path
import hashlib
import sqlite3

import uuid
import hashlib
from pathlib import Path
import sqlite3

def test_get_photo_image(test_app):
    filename = f"imgfile_{uuid.uuid4().hex}.jpeg"
    fake_image = uuid.uuid4().bytes
    test_hash = hashlib.sha256(fake_image).hexdigest()
    # No direct DB cleanup needed; test isolation ensures a clean DB
    # Upload
    resp = test_app.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
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
    # Cleanup: remove the uploaded file if it exists (should be isolated by temp_photos_dir)
    ext = Path(filename).suffix
    file_path = temp_photos_dir / f"{data['hash']}{ext}"
    if file_path.exists():
        file_path.unlink()
