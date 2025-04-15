from pathlib import Path
import hashlib
import sqlite3

def test_upload_photo(client, tmp_path):
    filename = "test_upload.jpeg"
    fake_image = b"fakeimgcontent"
    # Pre-test cleanup: remove any existing file/row with this hash+filename
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

    response = client.post(
        "/photos",
        files={"file": (filename, fake_image, "image/jpeg")}
    )
    assert response.status_code == 201
    data = response.json()
    # 1. Response fields
    assert "hash" in data
    assert data["filename"] == filename
    assert data.get("caption") is None
    # 2. File exists and contents match hash
    images_dir = Path(__file__).parent.parent / "images"
    ext = Path(filename).suffix
    hashed_filename = f"{data['hash']}{ext}"
    file_path = images_dir / hashed_filename
    assert file_path.exists()
    with file_path.open("rb") as f:
        saved = f.read()
    assert saved == fake_image
    # 3. DB record exists
    db_path = Path(__file__).parent.parent / "photos.db"
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT filename, hash, caption FROM photos WHERE hash=? AND filename=?", (data["hash"], filename)).fetchone()
    conn.close()
    assert row is not None
    assert row[0] == filename
    assert row[1] == data["hash"]
    assert row[2] is None
    # Cleanup
    file_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE hash=? AND filename=?", (data["hash"], filename))
    conn.commit()
    conn.close()
