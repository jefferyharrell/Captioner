import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import get_db, Base
from app.main import create_app

@pytest.fixture(scope="function")
def temp_photos_dir(tmp_path):
    photos_dir = tmp_path / "photos"
    photos_dir.mkdir()
    return photos_dir

@pytest.fixture(scope="function")
def test_app(temp_photos_dir):
    db_fd, db_path = tempfile.mkstemp()
    engine = create_engine(f"sqlite:///{db_path}")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    app = create_app(photos_dir=temp_photos_dir)
    app.state.db_sessionmaker = TestingSessionLocal
    with TestClient(app) as client:
        yield client
    os.close(db_fd)
    os.unlink(db_path)
