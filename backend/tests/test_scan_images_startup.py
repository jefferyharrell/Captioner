from pathlib import Path
import hashlib
import sqlite3
import uuid
import sqlite3
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import create_app


def test_scan_ignores_non_image_files(test_app, temp_photos_dir):
    """
    Put a non-image file in photos/, start the app (TestClient), and assert the file is NOT added to the DB.
    """
    filename = f"notanimage_{uuid.uuid4().hex}.txt"
    fake_file = b"notanimagecontent"
    file_path = temp_photos_dir / filename
    file_path.write_bytes(fake_file)
    # Start the app (should scan on startup)
    resp = test_app.get("/photos")
    assert resp.status_code == 200
    photos = resp.json()
    assert all(p["filename"] != filename for p in photos)


import pytest


def test_scan_images_at_startup(temp_photos_dir):
    """
    Put a new image file in photos/, ensure DB is empty for it, start the app (TestClient), and assert DB record is created after startup scan.
    """
    filename = f"startupscan_{__import__('uuid').uuid4().hex}.jpeg"
    fake_image = b"startupscancontent"
    test_hash = __import__("hashlib").sha256(fake_image).hexdigest()
    ext = Path(filename).suffix
    hashed_filename = f"{test_hash}{ext}"
    file_path = temp_photos_dir / hashed_filename
    file_path.write_bytes(fake_image)

    # Now instantiate the app/TestClient so the scan sees the file
    from app.main import create_app
    from app.db import Base
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import tempfile
    from fastapi.testclient import TestClient
    import os

    db_fd, db_path = tempfile.mkstemp()
    engine = create_engine(f"sqlite:///{db_path}")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    app = create_app(photos_dir=temp_photos_dir)
    app.state.db_sessionmaker = TestingSessionLocal
    with TestClient(app) as client:
        resp = client.get("/photos")
        assert resp.status_code == 200
        photos = resp.json()
        match = next(
            (
                p
                for p in photos
                if p["hash"] == test_hash and p["filename"] == hashed_filename
            ),
            None,
        )
        assert match is not None
        assert match["caption"] is None
    os.close(db_fd)
    os.unlink(db_path)
