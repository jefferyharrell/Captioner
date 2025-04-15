from pathlib import Path
import hashlib
import sqlite3

import uuid
import hashlib
from pathlib import Path
import sqlite3

def test_get_photo_image(client):
    filename = f"imgfile_{uuid.uuid4().hex}.jpeg"
    fake_image = uuid.uuid4().bytes
    test_hash = hashlib.sha256(fake_image).hexdigest()
    # Clean up DB and image file before upload
    db_path = Path(__file__).parent.parent / "photos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE hash=?", (test_hash,))
    conn.commit()
    conn.close()
    images_dir = Path(__file__).parent.parent / "images"
    ext = Path(filename).suffix
    hashed_filename = f"{test_hash}{ext}"
    file_path = images_dir / hashed_filename
    if file_path.exists():
        file_path.unlink()
    # Upload
    resp = client.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp.status_code == 201
    data = resp.json()
    # GET image
    resp2 = client.get(f"/photos/{data['hash']}/image")
    assert resp2.status_code == 200
    assert resp2.headers["content-type"].startswith("image/")
    assert resp2.content == fake_image
    # GET with fake hash/filename
    resp3 = client.get("/photos/badhash/doesnotexist.jpg/image")
    assert resp3.status_code == 404
    # Cleanup
    images_dir = Path(__file__).parent.parent / "images"
    ext = Path(filename).suffix
    file_path = images_dir / f"{data['hash']}{ext}"
    if file_path.exists():
        file_path.unlink()
    db_path = Path(__file__).parent.parent / "photos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE hash=? AND filename=?", (data["hash"], filename))
    conn.commit()
    conn.close()
