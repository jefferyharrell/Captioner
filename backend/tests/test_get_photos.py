from pathlib import Path
import hashlib
import sqlite3

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
    # Both uploaded photos should be present
    for up in uploaded:
        match = next((p for p in photos if p["hash"] == up["hash"] and p["filename"] == up["filename"]), None)
        assert match is not None
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
        conn.execute("DELETE FROM photos WHERE hash=? AND filename=?", (up["hash"], up["filename"]))
        conn.commit()
        conn.close()
