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
def test_app(tmp_path, temp_photos_dir):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    app = create_app(photos_dir=temp_photos_dir)
    app.state.db_sessionmaker = TestingSessionLocal
    with TestClient(app) as client:
        yield client
    if db_path.exists():
        db_path.unlink()
