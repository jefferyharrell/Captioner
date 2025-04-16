from pathlib import Path
import hashlib

from sqlalchemy import text

def test_upload_photo(test_app, temp_photos_dir):
    filename = "test_upload.jpeg"
    fake_image = b"fakeimgcontent"
    test_hash = hashlib.sha256(fake_image).hexdigest()
    ext = Path(filename).suffix
    hashed_filename = f"{test_hash}{ext}"
    file_path = temp_photos_dir / hashed_filename

    resp = test_app.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp.status_code == 201
    data = resp.json()
    # 1. Response fields
    assert "hash" in data
    assert data["filename"] == filename
    assert data.get("caption") is None
    # 2. File exists and contents match hash
    file_path = temp_photos_dir / f"{data['hash']}{ext}"
    assert file_path.exists()
    with open(file_path, "rb") as f:
        assert f.read() == fake_image
    # 3. DB record exists (via ORM)
    SessionLocal = test_app.app.state.db_sessionmaker
    with SessionLocal() as session:
        row = session.execute(
            text("SELECT filename, hash, caption FROM photos WHERE hash=:hash AND filename=:filename"),
            {"hash": data["hash"], "filename": filename}
        ).fetchone()
        assert row is not None
        assert row[0] == filename
        assert row[1] == data["hash"]
        assert row[2] is None
