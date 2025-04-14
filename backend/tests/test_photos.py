import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure the backend directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

from pathlib import Path
import sqlite3
import hashlib

def test_upload_photo(client, tmp_path):
    filename = "test_upload.jpeg"
    fake_image = b"fakeimgcontent"
    response = client.post(
        "/photos",
        files={"file": (filename, fake_image, "image/jpeg")}
    )
    assert response.status_code == 201
    data = response.json()
    # 1. Response fields
    assert "id" in data
    assert data["filename"] == filename
    assert data.get("caption") is None
    assert "hash" in data
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
    row = conn.execute("SELECT id, filename, hash, caption FROM photos WHERE id=?", (data["id"],)).fetchone()
    conn.close()
    assert row is not None
    assert row[1] == filename
    assert row[2] == data["hash"]
    assert row[3] is None
    # Cleanup
    file_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE id=?", (data["id"],))
    conn.commit()
    conn.close()
