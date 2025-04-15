from pathlib import Path
import hashlib
import sqlite3

def test_get_photo_by_id(client):
    filename = "detail.jpeg"
    fake_image = b"detailimg"
    # Upload
    resp = client.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp.status_code == 201
    data = resp.json()
    # GET by hash+filename
    resp2 = client.get(f"/photos/{data['hash']}/{filename}")
    assert resp2.status_code == 200
    detail = resp2.json()
    assert detail["hash"] == data["hash"]
    assert detail["filename"] == filename
    assert detail["caption"] == data["caption"]
    # GET with fake hash/filename
    resp3 = client.get("/photos/badhash/doesnotexist.jpg")
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
