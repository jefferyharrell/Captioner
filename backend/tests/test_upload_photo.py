from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import hashlib
from typing import cast


def test_upload_photo(test_app: TestClient, temp_photos_dir: Path) -> None:
    filename = "test_upload.jpeg"
    fake_image = b"fakeimgcontent"
    test_hash = hashlib.sha256(fake_image).hexdigest()
    ext = Path(filename).suffix
    hashed_filename = f"{test_hash}{ext}"
    file_path = temp_photos_dir / hashed_filename

    resp = test_app.post(
        "/photos", files={"file": (filename, fake_image, "image/jpeg")}
    )
    assert resp.status_code == 201
    data = resp.json()
    # 1. Response fields
    assert "hash" in data
    assert data["filename"] == filename
    assert data.get("caption") is None
    # 2. File exists and contents match hash
    file_path = temp_photos_dir / data["filename"]
    assert file_path.exists()
    with open(file_path, "rb") as f:
        assert f.read() == fake_image
    # 3. DB record exists (via ORM)
    SessionLocal = cast(sessionmaker, test_app.app.state.db_sessionmaker)  # type: ignore[attr-defined]
    with SessionLocal() as session:  # type: ignore[assignment]
        from typing import Any

        row: tuple[Any, ...] = session.execute(  # type: ignore[assignment]
            text(
                "SELECT filename, hash, caption FROM photos WHERE hash=:hash AND filename=:filename"
            ),
            {"hash": data["hash"], "filename": filename},
        ).fetchone()
        assert row is not None
        assert row[0] == filename
        assert row[1] == data["hash"]
        assert row[2] is None
