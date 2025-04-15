from pathlib import Path
import hashlib
import sqlite3
import uuid

def test_patch_photo_caption(client):
    filename = f"caption_{uuid.uuid4().hex}.jpeg"
    fake_image = b"captionimg"
    test_hash = hashlib.sha256(fake_image).hexdigest()
    images_dir = Path(__file__).parent.parent / "images"
    ext = Path(filename).suffix
    hashed_filename = f"{test_hash}{ext}"
    file_path = images_dir / hashed_filename
    if file_path.exists():
        file_path.unlink()
    db_path = Path(__file__).parent.parent / "photos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE hash=? AND filename=?", (test_hash, filename))
    conn.commit()
    conn.close()
    # Upload
    resp = client.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp.status_code == 201
    data = resp.json()
    # PATCH caption
    new_caption = "A very cool caption!"
    resp2 = client.patch(f"/photos/{data['hash']}/{filename}/caption", json={"caption": new_caption})
    assert resp2.status_code == 200
    patched = resp2.json()
    assert patched["hash"] == data["hash"]
    assert patched["filename"] == filename
    assert patched["caption"] == new_caption
    # GET to verify
    resp3 = client.get(f"/photos/{data['hash']}/{filename}")
    assert resp3.status_code == 200
    detail = resp3.json()
    assert detail["caption"] == new_caption
    # PATCH with fake hash/filename
    resp4 = client.patch("/photos/badhash/doesnotexist.jpg/caption", json={"caption": "nope"})
    assert resp4.status_code == 404
    data4 = resp4.json()
    assert set(data4.keys()) == {"error", "message"}
    assert data4["error"] == "NotFound"
    assert isinstance(data4["message"], str)
    # Cleanup
    if file_path.exists():
        file_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE hash=? AND filename=?", (data["hash"], filename))
    conn.commit()
    conn.close()
