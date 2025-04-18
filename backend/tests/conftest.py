import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import create_app
from typing import Generator
from pathlib import Path
import shutil
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def temp_photos_dir(tmp_path: Path) -> Generator[Path, None, None]:
    photos_dir = tmp_path / "photos"
    photos_dir.mkdir()
    yield photos_dir
    # Cleanup
    shutil.rmtree(photos_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def test_app(
    tmp_path: Path, temp_photos_dir: Path
) -> Generator[TestClient, None, None]:
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    from app.db import Base

    Base.metadata.create_all(bind=engine)
    app = create_app(photos_dir=temp_photos_dir)
    app.state.db_sessionmaker = TestingSessionLocal
    with TestClient(app) as client:
        yield client
    # Only delete the DB after the app context is fully closed
    if db_path.exists():
        db_path.unlink()
