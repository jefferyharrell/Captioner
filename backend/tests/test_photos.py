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
import os


def test_login_success(client, monkeypatch):
    test_password = "super_secret_test_pw"
    monkeypatch.setenv("PASSWORD", test_password)
    resp = client.post("/login", json={"password": test_password})
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"success": True}


def test_login_failure(client, monkeypatch):
    test_password = "super_secret_test_pw"
    monkeypatch.setenv("PASSWORD", test_password)
    resp = client.post("/login", json={"password": "wrong_pw"})
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"success": False}


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

def test_upload_duplicate_photo(client):
    filename = "dupe.jpeg"
    fake_image = b"dupeimg"
    # First upload
    resp1 = client.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp1.status_code == 201
    data1 = resp1.json()
    # Second upload (same content)
    resp2 = client.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp2.status_code == 409
    # Cleanup
    images_dir = Path(__file__).parent.parent / "images"
    ext = Path(filename).suffix
    file_path = images_dir / f"{data1['hash']}{ext}"
    if file_path.exists():
        file_path.unlink()
    db_path = Path(__file__).parent.parent / "photos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE id=?", (data1["id"],))
    conn.commit()
    conn.close()

def test_get_photos(client):
    # Upload two photos with different content
    files = [
        ("photo1.jpeg", b"img1_unique_content"),
        ("photo2.jpeg", b"img2_different_content")
    ]
    uploaded = []
    for fname, data in files:
        resp = client.post("/photos", files={"file": (fname, data, "image/jpeg")})
        assert resp.status_code == 201
        uploaded.append(resp.json())
    # GET /photos
    resp = client.get("/photos")
    assert resp.status_code == 200
    photos = resp.json()
    ids = {p["id"] for p in photos}
    # Both uploaded photos should be present
    for up in uploaded:
        assert up["id"] in ids
        match = next(p for p in photos if p["id"] == up["id"])
        assert match["filename"] == up["filename"]
        assert match["hash"] == up["hash"]
        assert match["caption"] == up["caption"]
    # Cleanup
    images_dir = Path(__file__).parent.parent / "images"
    db_path = Path(__file__).parent.parent / "photos.db"
    for up in uploaded:
        ext = Path(up["filename"]).suffix
        file_path = images_dir / f"{up['hash']}{ext}"
        if file_path.exists():
            file_path.unlink()
        conn = sqlite3.connect(db_path)
        conn.execute("DELETE FROM photos WHERE id=?", (up["id"],))
        conn.commit()
        conn.close()

def test_get_photo_by_id(client):
    filename = "detail.jpeg"
    fake_image = b"detailimg"
    # Upload
    resp = client.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp.status_code == 201
    data = resp.json()
    # GET by id
    resp2 = client.get(f"/photos/{data['id']}")
    assert resp2.status_code == 200
    detail = resp2.json()
    assert detail["id"] == data["id"]
    assert detail["filename"] == filename
    assert detail["hash"] == data["hash"]
    assert detail["caption"] == data["caption"]
    # GET with fake id
    resp3 = client.get("/photos/doesnotexist")
    assert resp3.status_code == 404
    # Cleanup
    images_dir = Path(__file__).parent.parent / "images"
    ext = Path(filename).suffix
    file_path = images_dir / f"{data['hash']}{ext}"
    if file_path.exists():
        file_path.unlink()
    db_path = Path(__file__).parent.parent / "photos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE id=?", (data["id"],))
    conn.commit()
    conn.close()

def test_patch_photo_caption(client):
    filename = "caption.jpeg"
    fake_image = b"captionimg"
    # Upload
    resp = client.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp.status_code == 201
    data = resp.json()
    # PATCH caption
    new_caption = "A very cool caption!"
    resp2 = client.patch(f"/photos/{data['id']}/caption", json={"caption": new_caption})
    assert resp2.status_code == 200
    patched = resp2.json()
    assert patched["id"] == data["id"]
    assert patched["caption"] == new_caption
    # GET to verify
    resp3 = client.get(f"/photos/{data['id']}")
    assert resp3.status_code == 200
    detail = resp3.json()
    assert detail["caption"] == new_caption
    # PATCH with fake id
    resp4 = client.patch("/photos/doesnotexist/caption", json={"caption": "nope"})
    assert resp4.status_code == 404
    # Cleanup
    images_dir = Path(__file__).parent.parent / "images"
    ext = Path(filename).suffix
    file_path = images_dir / f"{data['hash']}{ext}"
    if file_path.exists():
        file_path.unlink()
    db_path = Path(__file__).parent.parent / "photos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE id=?", (data["id"],))
    conn.commit()
    conn.close()

def test_get_photo_image(client):
    filename = "imgfile.jpeg"
    fake_image = b"imagedatahere"
    # Upload
    resp = client.post("/photos", files={"file": (filename, fake_image, "image/jpeg")})
    assert resp.status_code == 201
    data = resp.json()
    # GET image
    resp2 = client.get(f"/photos/{data['id']}/image")
    assert resp2.status_code == 200
    assert resp2.content == fake_image
    assert resp2.headers["content-type"] == "image/jpeg"
    # GET with fake id
    resp3 = client.get("/photos/doesnotexist/image")
    assert resp3.status_code == 404
    # Cleanup
    images_dir = Path(__file__).parent.parent / "images"
    ext = Path(filename).suffix
    file_path = images_dir / f"{data['hash']}{ext}"
    if file_path.exists():
        file_path.unlink()
    db_path = Path(__file__).parent.parent / "photos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE id=?", (data["id"],))
    conn.commit()
    conn.close()
