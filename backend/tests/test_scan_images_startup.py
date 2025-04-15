from pathlib import Path
import hashlib
import sqlite3
import uuid
import sqlite3
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import create_app

def test_scan_images_at_startup():
    """
    Put a new image file in images/, ensure DB is empty for it, start the app (TestClient), and assert DB record is created after startup scan.
    """
    filename = f"startupscan_{uuid.uuid4().hex}.jpeg"
    fake_image = b"startupscancontent"
    test_hash = __import__('hashlib').sha256(fake_image).hexdigest()
    images_dir = Path(__file__).parent.parent / "images"
    ext = Path(filename).suffix
    hashed_filename = f"{test_hash}{ext}"
    file_path = images_dir / hashed_filename
    if not images_dir.exists():
        images_dir.mkdir(parents=True)
    # Remove file and DB row if they exist
    if file_path.exists():
        file_path.unlink()
    db_path = Path(__file__).parent.parent / "photos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE hash=? AND filename=?", (test_hash, hashed_filename))
    conn.commit()
    conn.close()
    # Write the file
    with open(file_path, "wb") as f:
        f.write(fake_image)
    # Start the app (triggers startup event)
    with TestClient(create_app()):
        pass
    # Check DB for record
    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT filename, hash, caption FROM photos WHERE hash=? AND filename=?", (test_hash, hashed_filename)).fetchone()
    conn.close()
    assert row is not None, "Photo record not created at startup"
    assert row[0] == hashed_filename
    assert row[1] == test_hash
    assert row[2] is None
    # Cleanup
    if file_path.exists():
        file_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE hash=? AND filename=?", (test_hash, hashed_filename))
    conn.commit()
    conn.close()
