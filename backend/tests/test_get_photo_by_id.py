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

    photos_dir = Path(__file__).parent.parent / "photos"
    ext = Path(filename).suffix
    file_path = photos_dir / f"{data['hash']}{ext}"
    
    if file_path.exists():
        file_path.unlink()
    db_path = Path(__file__).parent.parent / "photos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE hash=? AND filename=?", (data["hash"], filename))
    conn.commit()
    conn.close()
