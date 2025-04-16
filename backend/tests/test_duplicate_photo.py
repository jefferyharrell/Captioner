from pathlib import Path
import hashlib
import sqlite3
import uuid

def test_upload_duplicate_photo(client, cleanup_files):
    filename = f"dupe_{uuid.uuid4().hex}.jpeg"
    fake_image = b"dupeimg"
    test_hash = hashlib.sha256(fake_image).hexdigest()
    photos_dir = Path(__file__).parent.parent / "photos"
    ext = Path(filename).suffix
    hashed_filename = f"{test_hash}{ext}"
    file_path = photos_dir / hashed_filename
    cleanup_files(file_path)
    if file_path.exists():
        file_path.unlink()
    db_path = Path(__file__).parent.parent / "photos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE hash=? AND filename=?", (test_hash, filename))
    conn.commit()
    conn.close()
    # First upload
    resp1 = client.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp1.status_code == 201
    data1 = resp1.json()
    # Second upload (same content)
    resp2 = client.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp2.status_code == 409
    data2 = resp2.json()
    assert set(data2.keys()) == {"error", "message"}
    assert data2["error"] in ("Conflict", "AlreadyExists", "Duplicate")
    assert isinstance(data2["message"], str)
    # Cleanup
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE hash=? AND filename=?", (test_hash, filename))
    conn.commit()
    conn.close()
