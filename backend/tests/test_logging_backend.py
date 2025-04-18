import os
import re
import tempfile
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import create_app
from app.db import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_logging_image_scan(tmp_path, monkeypatch):
    """
    Ensure that image scan logs to the log file when a new image is found.
    """
    # Setup temp log dir
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("SYSLOG_ENABLE", "0")
    monkeypatch.setenv("LOG_DIR", str(log_dir))

    # Setup temp photos dir
    photos_dir = tmp_path / "photos"
    photos_dir.mkdir()
    # Create a fake image file
    fake_image = b"logscancontent"
    filename = "logscan.jpeg"
    test_hash = __import__("hashlib").sha256(fake_image).hexdigest()
    hashed_filename = f"{test_hash}.jpeg"
    file_path = photos_dir / hashed_filename
    file_path.write_bytes(fake_image)

    # Setup temp DB
    db_fd, db_path = tempfile.mkstemp()
    engine = create_engine(f"sqlite:///{db_path}")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    # Re-initialize logging so it uses the temp log dir
    from app.logging_config import setup_logging

    setup_logging()

    # Reload image_utils so its logger attaches to the new handlers
    import importlib
    from app import image_utils

    importlib.reload(image_utils)

    # Create app with temp dirs
    app = create_app(photos_dir=photos_dir)
    app.state.db_sessionmaker = TestingSessionLocal
    with TestClient(app):
        pass  # triggers scan on startup

    # Check log file for image created log
    log_file = log_dir / "server.log"
    assert log_file.exists(), "Log file was not created."
    log_content = log_file.read_text()
    pattern = rf"Image created: {re.escape(str(file_path))} \(sha256={test_hash}\)"
    assert re.search(
        pattern, log_content
    ), f"Expected log line not found. Log content:\n{log_content}"

    os.close(db_fd)
    os.unlink(db_path)
