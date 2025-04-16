from pathlib import Path
import hashlib
import sqlite3
import uuid
import time
from fastapi.testclient import TestClient
from app.main import create_app

def test_detects_new_image_file_at_runtime(cleanup_files):
    """
    Start the app, drop a new image file into photos/, wait, and assert it is added to the DB (should fail until watchdog is implemented).
    """
    filename = f"runtime_added_{uuid.uuid4().hex}.jpeg"
    fake_image = b"runtimeimagecontent"
    test_hash = hashlib.sha256(fake_image).hexdigest()
    photos_dir = Path(__file__).parent.parent / "photos"
    ext = Path(filename).suffix
    hashed_filename = f"{test_hash}{ext}"
    file_path = photos_dir / hashed_filename
    if not photos_dir.exists():
        photos_dir.mkdir(parents=True)
    # Remove file and DB row if they exist
    if file_path.exists():
        file_path.unlink()
    db_path = Path(__file__).parent.parent / "photos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE hash=? AND filename=?", (test_hash, hashed_filename))
    conn.commit()
    conn.close()
    cleanup_files(file_path)
    # Start the app (leave running)
    with TestClient(create_app()):
        # Drop the file in while app is running
        with open(file_path, "wb") as f:
            f.write(fake_image)
        # Wait for watchdog/event system to (eventually) process the new file
        time.sleep(5)  # Increased to 5 seconds for watchdog to detect the event
        # Check DB for record
        conn = sqlite3.connect(db_path)
        row = conn.execute("SELECT filename, hash, caption FROM photos WHERE hash=? AND filename=?", (test_hash, hashed_filename)).fetchone()
        conn.close()
        assert row is not None, "Photo record not created at runtime (should fail until watchdog is implemented)"
        assert row[0] == hashed_filename
        assert row[1] == test_hash
        assert row[2] is None
    # Cleanup
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM photos WHERE hash=? AND filename=?", (test_hash, hashed_filename))
    conn.commit()
    conn.close()
