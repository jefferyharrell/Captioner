from pathlib import Path
import hashlib
import sqlite3

def test_get_photo_image(client):
    filename = "imgfile.jpeg"
    fake_image = b"imagedatahere"
    # Upload
    resp = client.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp.status_code == 201
    data = resp.json()
    # GET image
    resp2 = client.get(f"/photos/{data['hash']}/{filename}/image")
    assert resp2.status_code == 200
    assert resp2.content == fake_image
    assert resp2.headers["content-type"] == "image/jpeg"
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
