import pytest
from pathlib import Path


class DummyDB:
    def rollback(self):
        self.rolled_back = True


def test_scan_photos_folder_on_startup_non_integrity_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # Create a dummy image file
    img_path = tmp_path / "test.png"
    img_path.write_bytes(b"fakeimg")
    # Patch add_photo to raise a ValueError (not IntegrityError)
    monkeypatch.setattr(
        "app.image_utils.add_photo",
        lambda db, sha, fn, caption=None: (_ for _ in ()).throw(ValueError("fail!")),  # type: ignore
    )
    # Patch get_photo_by_hash to always return None
    monkeypatch.setattr("app.image_utils.get_photo_by_hash", lambda db, sha: None)  # type: ignore
    caplog.set_level("ERROR")
    with pytest.raises(ValueError):
        from app.image_utils import scan_photos_folder_on_startup

        scan_photos_folder_on_startup(tmp_path, object())
    assert any(
        "Error adding photo during scan" in r.getMessage() for r in caplog.records
    )


def test_scan_photos_folder_on_startup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # Create a dummy image file
    img_path = tmp_path / "image1.jpg"
    img_path.write_bytes(b"fake data")
    # Patch get_image_file_path to return our image
    monkeypatch.setattr(
        "app.image_utils.get_image_file_path",
        lambda db, sha, fn, caption=None: img_path,  # type: ignore
    )
    # Patch add_photo to do nothing
    monkeypatch.setattr(
        "app.crud.add_photo",
        lambda db, sha, fn, caption=None: None,  # type: ignore
    )
    caplog.set_level("INFO")
    from app.image_utils import scan_photos_folder_on_startup

    class MockQuery:
        def filter_by(self, **kwargs):
            return self

        def first(self):
            return None

    class MockDB:
        def query(self, *args, **kwargs):
            return MockQuery()

        def add(self, obj):
            pass

        def commit(self):
            pass

        def refresh(self, obj):
            pass

        def rollback(self):
            pass

    scan_photos_folder_on_startup(tmp_path, MockDB())
    assert any("Image created:" in r.getMessage() for r in caplog.records)
