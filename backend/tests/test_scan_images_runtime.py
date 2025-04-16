from pathlib import Path
import hashlib
import sqlite3
import uuid
import time
from fastapi.testclient import TestClient
from app.main import create_app

import pytest
import time

def test_detects_new_image_file_at_runtime(temp_photos_dir):
    """
    Start the app, then drop a new image file into photos/, poll /photos, and assert it is added to the DB.
    """
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
        img_path = temp_photos_dir / "runtime1.jpg"
        img_path.write_bytes(b"runtimeimg1")
        found = False
        for _ in range(10):  # poll for up to 5 seconds
            time.sleep(0.5)
            resp = client.get("/photos")
            assert resp.status_code == 200
            photos = resp.json()
            if any(p["filename"] == "runtime1.jpg" for p in photos):
                found = True
                break
        assert found, "runtime1.jpg was not detected by the backend within 5 seconds."
    os.close(db_fd)
    os.unlink(db_path)
