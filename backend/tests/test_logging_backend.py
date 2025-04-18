import os
import re
import tempfile
import logging
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import create_app
from app.db import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Any
import pytest
from pytest import MonkeyPatch


def test_syslog_handler_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[Any]
) -> None:
    """
    Simulate SysLogHandler setup failure and verify warning is logged to stderr.
    """

    class DummySysLogHandler:
        def __init__(self, *a: Any, **kw: Any) -> None:
            raise RuntimeError("syslog fail!")

    monkeypatch.setattr(logging.handlers, "SysLogHandler", DummySysLogHandler)  # type: ignore[attr-defined]
    monkeypatch.setenv("SYSLOG_ENABLE", "1")
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    from app.logging_config import setup_logging

    setup_logging()
    captured = capsys.readouterr()  # type: ignore
    err = captured.err  # type: ignore
    assert "Syslog handler could not be attached" in err


def test_log_file_truncation_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Simulate failure to truncate log file (open throws), should raise OSError.
    """
    import builtins

    real_open = builtins.open

    def bad_open(*a: Any, **kw: Any):  # type: ignore
        if a and isinstance(a[0], str) and a[0].endswith("server.log"):
            raise OSError("nope")
        return real_open(*a, **kw)  # type: ignore

    monkeypatch.setattr(builtins, "open", bad_open)  # type: ignore[attr-defined]
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    from app.logging_config import setup_logging

    with pytest.raises(OSError):
        setup_logging()


def test_syslog_handler_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Simulate successful syslog handler attach (no exception).
    """

    class DummySysLogHandler:
        level = 0

        def __init__(self, *a: Any, **kw: Any) -> None:
            pass

        def setFormatter(self, fmt: Any) -> None:
            pass

        def handle(self, record: Any) -> None:
            pass

    monkeypatch.setattr(logging.handlers, "SysLogHandler", DummySysLogHandler)  # type: ignore[attr-defined]
    monkeypatch.setenv("SYSLOG_ENABLE", "1")
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    from app.logging_config import setup_logging

    setup_logging()  # Should not raise or print warning


def test_logging_initialized_info(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[Any]
) -> None:
    """
    Ensure logging initialization info message is emitted (check stderr).
    """
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    from app.logging_config import setup_logging

    setup_logging()
    captured = capsys.readouterr()  # type: ignore
    out = captured.out  # type: ignore
    err = captured.err  # type: ignore
    assert "Logging initialized" in err or "Logging initialized" in out


def test_logging_image_scan(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
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
